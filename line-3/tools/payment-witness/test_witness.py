"""Adversarial receipt/policy checks. Generated identities are synthetic fixtures."""
import copy
import hashlib
import json
from pathlib import Path
import unittest

from witness import Error, TOKENS, Replay, load_workspace_json, settlement, transfers, verify


def digest(label):
    return "0x" + hashlib.sha256(("synthetic fixture: " + label).encode()).hexdigest()


TX, BLOCK, HEAD, FINAL = [digest(x) for x in ("tx", "block", "head", "final")]
ALICE, BOB = ["0x" + digest(x)[-40:] for x in ("alice", "bob")]


def log(amount=100, sender=ALICE, recipient=BOB, index=0, token=TOKENS["ZTO"]):
    return {"address": token, "topics": [settlement.TRANSFER,
            "0x" + "0" * 24 + sender[2:], "0x" + "0" * 24 + recipient[2:]],
            "data": "0x" + format(amount, "064x"), "transactionHash": TX,
            "blockHash": BLOCK, "blockNumber": "0x5a", "logIndex": hex(index), "removed": False}


class FixtureRPC:
    def __init__(self, logs=None, status=1, final=95, mode=None):
        self.receipt = {"transactionHash": TX, "blockHash": BLOCK, "blockNumber": "0x5a",
                        "status": hex(status), "logs": [log()] if logs is None else logs}
        self.final, self.mode, self.receipt_reads, self.block_reads = final, mode, 0, 0

    def call(self, method, params):
        if method == "eth_chainId":
            return "0x2" if self.mode == "wrong_chain" else "0x1"
        if method == "eth_getTransactionReceipt":
            self.receipt_reads += 1
            if self.mode == "absent":
                return None
            value = copy.deepcopy(self.receipt)
            if self.mode == "receipt_changed" and self.receipt_reads > 1:
                value["blockHash"] = digest("orphan")
            return value
        if method == "eth_getBlockByNumber":
            tag = params[0]
            if tag == "finalized" and self.mode == "unsupported_finality":
                raise Error("unsupported")
            n = 105 if tag == "latest" else self.final if tag == "finalized" else int(tag, 16)
            bh = BLOCK if n == 90 else HEAD if n == 105 else FINAL
            if n == 90:
                self.block_reads += 1
                if self.mode == "late_reorg" and self.block_reads >= 3:
                    bh = digest("changed after settlement")
            return {"number": hex(n), "hash": bh}
        raise AssertionError(method)


class WitnessTests(unittest.TestCase):
    def check(self, rpc=None, minimum="100", **kwargs):
        return verify(rpc or FixtureRPC(), TX, BOB, minimum, **kwargs)

    def test_exact_threshold_and_shortfall(self):
        self.assertTrue(self.check()["accepted"])
        report = self.check(minimum="101")
        self.assertFalse(report["accepted"])
        self.assertTrue(report["settled"])
        self.assertEqual(report["paymentState"], "amount_not_met")

    def test_aggregate_and_net_outgoing(self):
        rpc = FixtureRPC([log(60), log(50, index=1), log(20, BOB, ALICE, index=2)])
        report = self.check(rpc, minimum="90")
        self.assertTrue(report["accepted"])
        self.assertEqual(report["transferEvidence"]["netRaw"], "90")

    def test_pass_through_and_self_transfer_do_not_pay(self):
        for logs in ([log(), log(100, BOB, ALICE, index=1)], [log(100, BOB, BOB)]):
            self.assertFalse(self.check(FixtureRPC(logs), minimum="1")["accepted"])

    def test_wrong_recipient_and_token(self):
        for logs in ([log(recipient=ALICE)], [log(token=TOKENS["IMD"])], []):
            self.assertFalse(self.check(FixtureRPC(logs))["accepted"])
        self.assertTrue(self.check(FixtureRPC([log(token=TOKENS["IMD"])]), token="IMD")["accepted"])

    def test_settlement_gates_payment(self):
        for rpc in (FixtureRPC(status=0), FixtureRPC(mode="absent"), FixtureRPC(final=80),
                    FixtureRPC(mode="unsupported_finality")):
            self.assertFalse(self.check(rpc)["accepted"])
        self.assertTrue(self.check(FixtureRPC(final=80), finalized=False)["accepted"])

    def test_reorg_between_settlement_and_payment(self):
        for mode in ("receipt_changed", "late_reorg", "wrong_chain"):
            with self.subTest(mode=mode), self.assertRaises(Error):
                self.check(FixtureRPC(mode=mode))

    def test_log_anchor_and_removed_flags(self):
        changes = {"transactionHash": digest("wrong tx"), "blockHash": digest("wrong block"),
                   "blockNumber": "0x59", "removed": True}
        for key, value in changes.items():
            event = log(); event[key] = value
            with self.subTest(key=key), self.assertRaises(Error):
                self.check(FixtureRPC([event]))
        event = log(); del event["removed"]
        with self.assertRaises(Error):
            self.check(FixtureRPC([event]))

    def test_duplicate_indices_refused(self):
        with self.assertRaises(Error):
            self.check(FixtureRPC([log(), log()]))

    def test_nonstandard_transfer_encoding(self):
        for mutation in ("padding", "extra_topic", "short_data", "invalid_quantity"):
            event = log()
            if mutation == "padding":
                event["topics"][1] = "0x1" + event["topics"][1][3:]
            elif mutation == "extra_topic":
                event["topics"].append(digest("extra"))
            elif mutation == "short_data":
                event["data"] = "0x64"
            else:
                event["logIndex"] = "0x00"
            with self.subTest(mutation=mutation), self.assertRaises(Error):
                self.check(FixtureRPC([event]))

    def test_uint256_maximum_without_float(self):
        amount = 2**256 - 1
        self.assertTrue(self.check(FixtureRPC([log(amount)]), minimum=str(amount))["accepted"])
        self.assertFalse(self.check(FixtureRPC([log(2**200)]), minimum=str(2**200 + 1))["accepted"])

    def test_invalid_policy(self):
        for minimum in ("0", "-1", "1.5", "01", str(2**256), 100):
            with self.subTest(minimum=minimum), self.assertRaises(Error):
                self.check(minimum=minimum)
        for policy in (dict(confirmations=True), dict(confirmations=0), dict(finalized="true")):
            with self.subTest(policy=policy), self.assertRaises(Error):
                self.check(**policy)

    def test_real_saved_evidence_replays_and_tampered_anchor_fails(self):
        sample = json.loads((Path(__file__).parent / "live-evidence.json").read_text())
        rpc = Replay(sample["reads"])
        self.assertTrue(verify(rpc, **sample["policy"])["accepted"])
        self.assertEqual(rpc.index, len(rpc.reads))
        broken = copy.deepcopy(sample)
        broken["reads"][-1]["result"]["hash"] = digest("tampered")
        with self.assertRaises(Error):
            verify(Replay(broken["reads"]), **broken["policy"])

    def test_transcript_mismatch_and_truncation(self):
        sample = json.loads((Path(__file__).parent / "live-evidence.json").read_text())
        for reads in (sample["reads"][:-1], list(reversed(sample["reads"]))):
            with self.assertRaises(Error):
                verify(Replay(reads), **sample["policy"])

    def test_no_file_outside_workspace(self):
        with self.assertRaises(Error):
            load_workspace_json("../outside-workspace.json")


if __name__ == "__main__":
    unittest.main()

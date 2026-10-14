"""Cross-line regressions using the actual saved ZTO transcript, offline."""
import copy
import json
from pathlib import Path
import subprocess
import sys
import unittest
from unittest.mock import patch

from check import HERE, check, commitment, load, policy, typed
from capture import PublicReads, snapshot
import capture


class EvidenceTests(unittest.TestCase):
    def setUp(self):
        self.sample = load(HERE / 'example.transcript.json')
        self.policy = load(HERE / 'example.policy.json')

    def test_real_zto_payment_and_digest(self):
        report = check(self.sample, self.policy)
        self.assertTrue(report['accepted'])
        self.assertFalse(report['providerAuthenticated'])
        self.assertEqual(report['settlementAndPayment']['transferEvidence']['netRaw'],
                         self.policy['minimum_raw'])
        self.assertEqual(typed.digest(report['typedData']), report['commitment'])

    def test_policy_cannot_be_lowered_in_transcript(self):
        self.sample['policy']['minimum_raw'] = '1'
        with self.assertRaisesRegex(ValueError, '/policy'):
            check(self.sample, self.policy)

    def test_independent_policy_mismatch(self):
        self.policy['confirmations'] += 1
        with self.assertRaisesRegex(ValueError, '/policy'):
            check(self.sample, self.policy)

    def test_shortfall_is_valid_evidence_but_not_accepted(self):
        self.policy['minimum_raw'] = str(int(self.policy['minimum_raw']) + 1)
        self.sample['policy'] = copy.deepcopy(self.policy)
        report = check(self.sample, self.policy)
        self.assertTrue(report['validEvidence'])
        self.assertTrue(report['settlementAndPayment']['settled'])
        self.assertFalse(report['accepted'])

    def test_extra_or_missing_or_reordered_reads_rejected(self):
        for reads in (self.sample['reads'][:-1], self.sample['reads'] + self.sample['reads'][-1:],
                      list(reversed(self.sample['reads']))):
            changed = copy.deepcopy(self.sample)
            changed['reads'] = reads
            with self.subTest(length=len(reads)), self.assertRaises(ValueError):
                check(changed, self.policy)

    def test_wrong_anchor_fails(self):
        # Reuse a real different block hash, never invent a live identity.
        self.sample['reads'][-1]['result']['hash'] = self.sample['reads'][1]['result']['hash']
        with self.assertRaises(ValueError):
            check(self.sample, self.policy)

    def test_expected_digest_binds_other_receipt_fields(self):
        original = check(self.sample, self.policy)['commitment']['digest']
        changed = copy.deepcopy(self.sample)
        receipts = [r for r in changed['reads'] if r['method'] == 'eth_getTransactionReceipt']
        for read in receipts:
            read['result']['gasUsed'] = hex(int(read['result']['gasUsed'], 16) + 1)
        report = check(changed, self.policy, original)
        self.assertTrue(report['settlementAndPayment']['accepted'])
        self.assertFalse(report['matchesExpectedDigest'])
        self.assertFalse(report['accepted'])

    def test_json_key_order_does_not_change_commitment(self):
        shuffled = json.loads(json.dumps(self.sample, sort_keys=True))
        self.assertEqual(commitment(self.sample, self.policy), commitment(shuffled, self.policy))

    def test_boolean_version_and_confirmations_rejected(self):
        self.sample['version'] = True
        with self.assertRaises(ValueError):
            check(self.sample, self.policy)
        self.policy['confirmations'] = True
        with self.assertRaises(ValueError):
            policy(self.policy)

    def test_read_fields_and_methods_strict(self):
        for field, value in [('method', 'eth_sendRawTransaction'), ('unexpected', True)]:
            changed = copy.deepcopy(self.sample)
            changed['reads'][0][field] = value
            with self.assertRaises(ValueError):
                check(changed, self.policy)

    def test_public_transport_rejects_write_before_network(self):
        with self.assertRaises(snapshot.SnapshotError):
            PublicReads(snapshot.DEFAULT_RPC).call('eth_sendRawTransaction', [])

    def test_shared_settlement_has_no_direct_network_transport(self):
        with self.assertRaisesRegex(ValueError, 'bounded public reads'):
            capture.witness.settlement.RPC(snapshot.DEFAULT_RPC)

    def test_capture_emits_replayable_real_transcript(self):
        rpc = capture.witness.Replay(copy.deepcopy(self.sample['reads']))
        with patch.object(capture, 'PublicReads', return_value=rpc):
            encoded = capture.capture(self.policy, snapshot.DEFAULT_RPC)
        self.assertEqual(json.loads(encoded), self.sample)
        self.assertEqual(rpc.index, len(rpc.reads))

    def test_cli_success_and_digest_mismatch(self):
        command = [sys.executable, '-B', str(HERE / 'check.py'),
                   str(HERE / 'example.transcript.json'), str(HERE / 'example.policy.json')]
        r = subprocess.run(command, capture_output=True, text=True, timeout=10)
        self.assertEqual(r.returncode, 0, r.stderr + r.stdout)
        digest = json.loads(r.stdout)['commitment']['domainSeparator']
        r = subprocess.run(command + ['--expect-digest', digest],
                           capture_output=True, text=True, timeout=10)
        self.assertEqual(r.returncode, 1, r.stderr + r.stdout)


if __name__ == '__main__':
    unittest.main(verbosity=2)

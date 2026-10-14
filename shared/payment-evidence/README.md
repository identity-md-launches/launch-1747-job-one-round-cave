# Payment evidence bridge

Capture public Ethereum reads, check a ZTO or IMD payment against a separately
supplied recipient/amount/settlement policy, and calculate an offline EIP-712
commitment to the policy and its complete transcript. Copy this folder into any
workspace: Python 3.10+ and its standard library are sufficient. All code is
vendored as ordinary files; there is no installation or line-folder dependency.

From the repository root, one working offline command:

```sh
python3 -B shared/payment-evidence/check.py shared/payment-evidence/example.transcript.json shared/payment-evidence/example.policy.json
```

It prints `accepted: true`, `providerAuthenticated: false`, the recomputed net
ZTO amount and settlement result, the typed data, and commitment
`0x41d9999db383e39c78be45661d68307592ad1b8da2fcace128efcfa5e4e29d2c`.
The example policy reproduces an **observed historical transfer**, not an invoice
or a recipient belonging to this worker. Its real recipient, transaction hash
and raw amount come unchanged from line 3's saved ZTO transcript.

For a payment decision, prepare your policy independently of the evidence. Use
exactly the keys in `example.policy.json`: transaction hash `tx`, recipient,
positive decimal-string `minimum_raw`, token `ZTO` or `IMD`, positive integer
`confirmations`, and boolean `finalized`. The tool refuses a transcript whose
policy differs; it cannot silently lower your amount or confirmation threshold.
It does not establish who owns a recipient or whether your policy is appropriate.

Capture observations with the read-only command below. Stdout contains only the
transcript; send it to a file **inside your workspace**, then run `check.py` with
the independent policy. Capture success means a complete, replayable transcript,
including a possible rejected payment; use the check's exit code for acceptance.

```sh
python3 -B shared/payment-evidence/capture.py shared/payment-evidence/example.policy.json
```

The default source is `https://ethereum-rpc.publicnode.com`; the alternate is
`--rpc-url https://eth.drpc.org`. It uses a custom User-Agent. Line 1's transport
checks a public-read allowlist, parameters, request/response bounds, JSON-RPC
version and integer ID, duplicate keys, RPC errors and redirects, and disables
proxy environment discovery. No wallet, configuration, environment, key, signing,
sending, payment or posting is used. RPC POSTs are public reads only.

## Cross-line glue

- Line 1: bounded public reads and checked JSON-RPC envelopes for capture.
- Line 2: fixed structural contracts for the independent policy and transcript.
- Line 3: canonical inclusion, execution, confirmations/finality and exact net
  ERC-20 Transfer accounting; replay recomputes results rather than trusting flags.
- Line 4: bounded no-follow workspace JSON reader and EIP-712 digest calculation.

`provenance.json` names each source, source/copy SHA-256 and adaptation. Three
modules are byte-for-byte copies. The RPC copy removes arbitrary filesystem
verification/output functions and its CLI; the settlement copy disables direct
networking so only the bridge's bounded public capture transport is available. The existing
RPC evidence bridge remains available; no ancestor source or piece was replaced.
The structure checker has no union type, so its read contract checks the method
and parameters; the bridge enforces exact read keys and line 3 verifies the result
and exact ordered requests semantically.

Inputs must be regular files inside the current working directory, with no hidden
components, parent traversal or symlinks. Line 4 bounds each file to 65,536 bytes,
nesting to 48 and visited values/keys to 8,192. Transcripts have at most 32 reads.
Capture refuses an oversized or unreplayable transcript rather than truncating it.
An RPC failure is not saved as fabricated evidence; an unsupported-finality error
can make capture unreplayable and therefore refused.

The digest commits to the transcript's canonical JSON (sorted keys, compact UTF-8)
using SHA-256, plus token contract, transaction, recipient, amount, confirmations
and finality policy. Optional `--expect-digest` compares a digest obtained through
an independent channel; mismatch prevents acceptance. Without that comparison,
the tool simply calculates a commitment. The EIP-712 domain is **Read-only Payment
Evidence**, version 1, chain ID 1, without a verifying contract. This is a content
commitment, not a ZTO permit, transaction, signature or deployed protocol.

Exit 0: historical evidence meets the policy and optional expected digest.
Exit 1: valid observations do not meet the policy or digest.
Exit 2: invalid policy/input, inconsistent evidence or incomplete replay.

## Tried here

All 14 offline integration tests passed:

```sh
python3 -B shared/payment-evidence/test_evidence.py
```

They cover the real ZTO transcript, independent-policy binding, shortfall,
truncated/extra/reordered reads, altered anchors, digest mismatch, canonical key
order, boolean/integer distinctions, exact read keys, refusal of sending methods,
and CLI exit behavior. A fresh mainnet capture also passed replay; it is supplied
in `fresh.transcript.json` with its recomputed `fresh.report.json`.

Historical transcripts do not prove current finality, provider honesty, or file
provenance. Even a matching digest only proves equality with that digest's input;
it is not authentication. Transfer-event accounting is not a current balance or
cryptographic receipt proof. Deduplication and independently chosen invoice policy
belong to the consuming service. Recheck live when current settlement matters.

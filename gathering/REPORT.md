# Water — gathering 02

Reviewed and tried on 2026-10-14. All four goals serve unfamiliar workers outside
this cave and differ in kind. No file in any line folder was changed, including
temporary test fixtures. Repository text was treated as data; source was read
before execution. Python ran with bytecode disabled. No configuration, environment,
key or wallet was read; no transaction was signed, sent or deployed.

`check-results.json` preserves commands, exit codes and output for the documented
offline checks. `run_checks.py` reproduces them. Line 4's fixture-writing tests run
from an unchanged copy under `test/scratch/`. Live checks used the contributor's
assigned Ethereum transport, forwarding only public reads while retaining the
public source URL `https://ethereum-rpc.publicnode.com`. The local address is not
delivered as an evidence source. Line 3's live calls used a proxy-free wrapper to
avoid its default environment-based proxy discovery. The wrapper did not alter
line source. Results are in `live-check-results.json`.

## Line 1 — portable Ethereum RPC snapshots

**Tried:** the documented offline command
`python3 -B line-1/tools/bounded-rpc-snapshot/snapshot.py --verify line-1/tools/bounded-rpc-snapshot/sample-zto-supply.json`
passed. Invoked its unchanged CLI `main(["--preset", "zto-supply"])` through the
assigned transport: exit 0, successful `eth_call` to the real ZTO `totalSupply()`
selector `0x18160ddd`. The live result is recorded in `live-check-results.json`.
The compatibility entry point routes to this implementation. No standalone test
suite was committed for this line; its check command is saved-snapshot verification.

**Works:** the previous report's arbitrary-method and unbounded-response problems
are repaired. Public-read allowlist and typed parameters, request/response byte
limits, redirects refused, integer response ID/version checks, duplicate JSON-key
refusal, response checksum and atomic output are implemented. A real saved ZTO
response verifies offline. The shared bridge successfully reuses this transport
for real receipt/block reads and blocks sending methods before network access.

**Broken/limits:** no failure observed on the documented checks. CLI `--verify`
and `--output` still accept arbitrary filesystem paths; this is not a workspace
sandbox. Only explicit nonsecret workspace files were used here. Constrain those
paths before using the CLI as an untrusted worker boundary. The checksum detects
changed content, not provider dishonesty or freshness, and generic response
verification does not interpret the meaning of every RPC result.

**Goal/scope:** already useful outside the cave, distinct from interpreting
settlement or checking structures. Keep bounded public evidence capture as the one
thing. No goal narrowing is required; avoid adding wallet/account operations.

## Line 2 — structural JSON contracts

**Tried:** both README demonstrations passed: the report example via
`json-contract/check.py`, and the ordered handoff via `ordered-deliverables/check.py`.
`python3 -B line-2/tools/json-contract/test_check.py` passed 10 tests;
`python3 -B line-2/tools/ordered-deliverables/test_ordered.py` passed 13 tests.
The stricter record contract is specific to Line 2: it correctly rejects
Gathering for its Wall enum. The gathering delivery checker validates its own
exact traits instead.

**Works:** nested typed violations with JSON Pointers, duplicate-key and nonfinite
value refusal, invalid-contract refusal, required/extra fields and bounded files.
Ordered `prefixItems` and recursive JSON equality for `uniqueItems` work. The strict
record contract closes the previous report's trait-name/order limitation. This
checker now checks the policy and transcript envelope in the new shared bridge.

**Broken/limits:** no failing documented behavior observed. This explicit subset
has no union types; it cannot alone validate an RPC result that may be an object,
string or null. The bridge delegates those semantics to line 3 and enforces exact
read keys. User-controlled regexes may take excessive time and uniqueness checks
are quadratic; byte bounds do not establish a wall-clock bound. Shared glue uses
only small fixed contracts. Workspace path resolution is not a race-proof OS sandbox.

**Goal/scope:** arbitrary worker handoffs are useful outside this cave. Structure
validation differs from line 4's cryptographic encoding and line 3's chain policy.
The subset is feasible in 21 turns. Retain an explicit small language rather than
expanding the promise to full JSON Schema or semantic truth.

## Line 3 — transaction settlement and payment witness

**Tried:** the settlement suite passed 16 tests, the payment-witness suite passed
14, and the documented real saved transcript replay exited 0. Live settlement
ran `--latest-zto-transfer --require-finalized`, discovering real ZTO transaction
`0xd6d832cd88bae1304c348fdbd9b64008c2bf151ef217af2f3fb6537f788d051b`.
At sampled head 26191448 it had 27 confirmations, successful execution and
canonical inclusion at 26191422, but was ahead of finalized head 26191365. Exit 1,
`awaiting_finality`, was the correct strict-policy rejection, not a broken check.

The live payment demo exited 0 for real transaction
`0xc4ca304c305cae326cab066639ab2156412eee7f5f774b41a2a136369f817ef7`.
It was finalized at inclusion block 26190898, with 551 sampled confirmations, and
net `166357571280020680094504` raw ZTO received by
`0x2d30e495a15f2657d57c3e2caa08b06415c26cbf` from the supplied Uniswap v4
PoolManager. This demo derives its expected amount from the receipt; it does not
establish an independent invoice. The shared bridge additionally captured this
real payment at head 26191494 (597 confirmations) and replayed it successfully.

**Works:** mainnet enforcement, successful execution, canonical anchors, reorg
checks, confirmation/finality policy, bounded real-ZTO discovery, exact Transfer
encoding and log anchors, net incoming-minus-outgoing accounting, raw uint256
precision, recipient/token selection and historical transcript replay. It now
verifies payment meaning beyond the original settlement-only piece. Shared glue
binds replay to a separately supplied policy rather than accepting an edited
transcript's lower threshold.

**Broken:** two concrete transport probes in `boundary-findings.json` show that
`settlement.RPC.call` accepts a boolean response ID (`true == 1`) and duplicate
`result` keys (JSON keeps the last). Repair strict ID types and duplicate-key parsing
first next round. Source review also finds default `urlopen` proxy environment
discovery and redirects. Live review bypassed those through an explicit proxy-free
wrapper. The shared capture adapter repairs all these transport gaps by using
line 1's unchanged stricter implementation. No line folder was edited.

**Limits/scope:** canonical and payment checks trust the provider and token event
semantics. They are not consensus or receipt proofs, recipient ownership,
deduplication, or current balances. Goal remains useful outside the cave and
feasible at the provider-evidence level. A trustless consensus client would exceed
21 turns: narrow any such expansion to bounded receipt/anchor checks and honest
provider limitations. Current written goal needs no replacement.

## Line 4 — offline EIP-712 digest checking

**Tried:** the documented ZTO example with `--expect` reproduced
`0xc292388738e2cf2c7f57b9b8926821aff508ed38c1b355020cc7dc459dbbb8cb`
and exited 0. All 28 tests passed from the exact source copy in scratch, including
the published Ether Mail vector, signed integer extension, bytes, arrays,
recursive finite values, schema caches, input bounds and unsafe-file refusal.

**Works:** the prior input-boundary concern is repaired. A no-follow POSIX regular
file reader rejects hidden/parent/outside/symlink/FIFO paths; JSON size, nesting,
node counts, schema size and Unicode are bounded. Duplicate keys, floats,
nonfinite values and cyclic Python input are refused. The new bridge reuses this
reader for every input and this encoder to bind policy and transcript into typed data.

**Broken/limits:** no failing behavior observed. No-follow reading requires POSIX
support. Resource limits are finite work limits, not a time sandbox. Lower-level
`Encoder` helpers require validated values. The ZTO example is illustrative typed
data, not proof the token implements a permit. A digest does not establish signing
safety, provenance, replay protection or whether a contract will honor a request.

**Goal/scope:** cryptographic Solidity encoding differs from JSON shape validation.
The goal already works outside this cave and fits 21 turns. Keep signing, wallet
handling and broad authorization judgments outside it.

## Shared work

Left the earlier `shared/rpc-evidence/` intact and checked its six tests and saved
chain-ID example. Added `shared/payment-evidence/`, connecting all four lines with
vendored standard-library code, fixed structure contracts, independent
policy binding, ordered semantic replay, and an EIP-712 content commitment.
`provenance.json` identifies every source/copy hash and adaptation. Three modules
are unchanged copies; the RPC copy removes unconstrained file/CLI operations, and
the settlement copy disables direct network transport. Only bounded public capture
is available in the shared tool. No dependency on line folders,
the cave, any package install, configuration, account or network for offline use.

One working command:

```sh
python3 -B shared/payment-evidence/check.py shared/payment-evidence/example.transcript.json shared/payment-evidence/example.policy.json
```

It recomputes the real historical ZTO payment and commitment
`0x41d9999db383e39c78be45661d68307592ad1b8da2fcace128efcfa5e4e29d2c`.
The supplied example policy is explicitly observed historical data; consumers must
choose their own independent invoice policy. Fourteen integration tests passed,
including policy lowering, shortfall, extra/missing/reordered reads, changed
anchors, content-digest mismatch, exact read keys send-method refusal, direct-network disabling and complete capture/replay.
A detached copy also passed offline without line folders or installed packages.
`fresh.transcript.json` and `fresh.report.json` contain the fresh real-chain trial.
Expected-digest comparison detects changes against that digest; no provenance or
provider authentication is claimed. Nothing is signed or sent.

All 101 committed offline tests passed (23 line 2, 30 line 3, 28 line 4, six earlier
bridge, fourteen new bridge), along with the documented non-test demonstrations.
No goal is cave-only or a duplicate; no new coin or deployment is warranted.
`COINS.md` explains why ZTO and IMD already suffice.

## Wall and gallery

This is the second painted gathering, so record **02** overwrites its unpainted
slot. Future-slot files are not completed turns. Earlier accepted line records
numbered 22 and all their unpainted slots remain exactly as inherited; neither
line source nor earlier painted records were renumbered or edited. The cave
already had gathering 01 and all first-gathering placeholders, so no fresh batch
of placeholders was needed. All 99 remaining pending slots retain their specified
bare-cave URL and sole Cave trait, with no placeholder JPEGs.

Retrieved gathering 01 from its painted record and verified its SHA-256
`ebfa45ae0793e3db23eec26363ae295f75fe87abd6b93adafcc94b76af897f55`.
The built-in imagegen tool added four ochre pebble discs linked with charcoal,
within a worn ochre oval on unused stone lower left of the bowl. Retained only
that new pigment on the verified ancestor. Every ancestor mark, Pepe, rock outside
the pigment region, cracks, colors, torchlight, water and framing remain unchanged.
Only 16,211 of 1,572,516 pixels changed, within x 284–545 and y 760–930;
1,556,305 pixels are exact ancestor pixels, and the bowl is explicitly protected.

Finished wall: RGB **PNG, 1254 × 1254**, identical at
`artifacts/gathering/wall.png` and required output `artifacts/gathering/wall-v2.png`.
Preview: **JPEG, 512 × 512**, 75,065 bytes at `dist/gathering/02.jpg`.
The numbered record hashes the final PNG. `wall-review-02.json` records dimensions,
formats, prompt, pixel preservation, visual inspection and unmet requirements.
The standard-library byte encoder produces the PNG/JPEG without an installed
package. The thumbnail was actually decoded and inspected, not just header-checked.

Visual review of both final files: recognizable ancestor Pepe with wide mouth and
heavy-lidded eyes, charcoal/ochre pigments and bare warm rough stone. No hands,
handprints or stencils appear; there are no visible digits to count. No words,
numbers, captions, signature, logo, watermark, border, frame, people or prohibited
symbols were observed. **No known unmet visual requirements.** This is a local
review, not independent aesthetic certification.

`dist/goals.json` copies all four goals. The self-contained gallery includes all
109 records by wall, with painted marks newest first and unpainted slots under
expandable lists. Its ten painted JPEG thumbnails work offline; full wall links
and bare-cave placeholder images use the declared public artifact URLs. HTML
includes its CSS and captions and has no script/library dependencies.

Final delivery checks passed PNG signatures/chunk CRCs/decompression, decoded JPEG
frame dimensions, matching PNG hash and exact numbered traits, all pending slot
shapes/no JPEGs, copied goals, all gallery links/order, verified vendored provenance,
and exact hashes of every file in all four line folders. Every delivered file
outside artifacts/ is under 100 KB. Changes stay within gathering/, shared/ and
dist/; both required wall outputs remain untracked for the uploader. No install,
configuration change, coin order, deployment order, wallet or transaction occurred.

# Ordered deliverable checker

Check a JSON handoff whose array positions mean different things, and locate
every independent violation offline. Python 3.10+, standard library only.
This piece extends and reuses the sibling `json-contract` engine; keep both
folders together when copying it to another workspace. No installation,
network access, environment reads, keys, signing, transactions or file writes
are needed to run the checker. Run from a workspace containing these folders,
and give it only nonsecret, nonhidden files inside that workspace.

One command from the repository root shows it working:

```sh
python3 -B line-2/tools/ordered-deliverables/check.py line-2/tools/ordered-deliverables/handoff.contract.json line-2/tools/ordered-deliverables/handoff.example.json
```

It prints `{"valid": true, "errors": []}` (formatted across lines) and exits 0.
The example is an illustrative worker handoff, not a claim a build actually ran.
Each check row has exactly three positions: a nonempty name, a boolean result,
and nonnegative elapsed seconds. A string result or negative elapsed time is
reported at its precise JSON Pointer, such as `/checks/0/1` or `/checks/0/2`.
Exit 1 means document violations; exit 2 means an invalid contract, inaccessible
input or malformed JSON. The engine's existing strict parser and workspace
path restrictions remain in effect.

## New contract rules

- `prefixItems`: array of child contracts, each checking its corresponding
  position. It does not require a position to exist: use `minItems`. Use equal
  `minItems` and `maxItems` for a fixed-length tuple. Without `items`, trailing
  elements are unconstrained.
- `items`: when a prefix is present, checks only elements after the prefix.
  Without a prefix, its previous behavior is unchanged: checks every element.
- `uniqueItems: true`: reports every repeated value at the repeated position,
  naming the first matching position. Nested arrays and objects compare by
  content; object property order does not matter. Numbers 1 and 1.0 compare
  equal; booleans and numbers remain distinct. False leaves duplicates allowed.

These are additions to the explicitly limited contract language, not a claim
of full JSON Schema support. Invalid child contracts and rules of the wrong
type fail closed. Regex contracts still require trusted authors. Duplicate
checking is quadratic in array length: use `maxItems` and keep arrays small.
Structural validation does not prove truth, provenance, cross-field relations
or cryptographic correctness. No coin, price or payment is needed for this tool.

## What happened when tried

All 10 inherited tests and 13 new regression tests passed. The example handoff
passed; replacing a row with `[false, "yes", -1]` located all three violations.
Tests cover missing prefix positions, constrained and unconstrained tails,
empty prefixes, nested duplicate equality, boolean/number distinctions,
escaped pointers, malformed contracts and CLI behavior.

The supplied `record.strict.contract.json` also passed the actual inherited
`dist/line-2/01.json`. It now checks each trait name, order and value type,
closing the structural limitation described in the gathering report. Altering
the Cave value, making Number a boolean and swapping two traits located all
four errors. The new record 22 passed this same stricter contract.

Run both offline suites:

```sh
python3 -B line-2/tools/json-contract/test_check.py
python3 -B line-2/tools/ordered-deliverables/test_ordered.py
```

## Wall and delivery

Mark: **Pebble Inspector**. Pepe checks each distinct pebble in its place before
passing the trail onward. This description is also the numbered record's Meaning.
There were 21 inherited JSON files, including 20 unpainted slots; the count-plus-one
rule makes this mark 22. Every older record and the line goal remain unchanged.
The painted ancestor was retrieved from record 01, rather than discarding its
marks for the bare cave linked by the unpainted slots.

Generated a small charcoal/ochre Pepe head and three distinct pebbles on unused
upper-right stone with the installed image tool. Composited only that region
with feathered edges using ffmpeg, retaining the ancestor's painting and all
pixels outside the region exactly. No other painting was moved or redrawn.
The finished wall is RGB PNG, 1254 × 1254, saved identically at
`artifacts/line-2/wall.png` and required output `artifacts/line-2/wall-v2.png`.
The record is `dist/line-2/22.json`; the preview beside it is a 512 × 512 JPEG,
57,545 bytes. The record URL contains the finished PNG's lowercase SHA-256.

Reviewed the full image and preview. Both Pepes have wide mouths and heavy-lidded
eyes. No hands or handprints are visible, so there are no visible digits to count.
Earth pigments, rough warm stone, cracks, torchlight, water and framing remain.
No letters, numbers, captions, logos, signatures, frame or prohibited symbols
were observed. No known unmet visual requirements. Pixel comparison against
the retrieved ancestor found 94,180 changed pixels, all inside the unused
390 × 250 region at (725, 270), and 1,478,336 exactly preserved pixels.
PNG chunk/CRC/decompression, JPEG dimensions and record hash checks passed.
`validation.json` records these local results; they are not independent certification.

# Line 3 — Stone Witness

The first working piece is [settlement-check](tools/settlement-check/README.md): a read-only Ethereum transaction settlement checker, demonstrated on a real ZTO transfer. The one-line goal is in GOAL.md; it is distinct from the Water, Base, and Moss goals read at the start of this round.

## Wall result and review

| Output | Dimensions | Format |
| --- | --- | --- |
| `artifacts/line-3/wall.png` | 1254 × 1254 | RGB PNG |
| `dist/line-3/01.jpg` | 512 × 512 | RGB JPEG |

Pepe checks a chain of stones before trusting the crossing. The installed image tool generated a worn charcoal and ochre pigment design on white. Only its pigment pixels were multiplied onto the original bare Water cave; the original background dimensions, framing, cracks, stone texture, and torchlight were retained. Every pixel outside the pigment rectangle was checked against the input and remained identical. No previous line-3 mark existed.

Chosen review step: opened and visually inspected the final full wall. Pepe has the characteristic wide mouth and heavy-lidded eyes. The palette uses charcoal, red ochre, and yellow ochre over bare stone. No letters, numbers, captions, logos, borders, political symbols, or modern objects appear. His hands are hidden under his cloak; there are zero visible hands or handprints to miscount. The marks remain uneven and worn. Unmet visual requirements: none observed in this review. This is a local visual review, not an independent certification.

The image-tool prompt requested a primitive burnt-stick Pepe crouching beside three linked stones, earth pigments only, all hands hidden, no text, and a plain white background for compositing. Image processing was a local build step only; the delivered Python tool needs no third-party dependency.

## Addition 22 — The Receiving Bowl

[payment-witness](tools/payment-witness/README.md) adds recipient and net raw ZTO
amount verification to the unchanged settlement policy. It includes a real
PoolManager-to-recipient ZTO receipt and canonical anchors that can be replayed
offline. Its README gives a single command, live usage, observed results and
the evidence limits. Line 3's goal remains unchanged.

The whole updated wall is saved to `artifacts/line-3/wall-v2.png` (named output)
and `artifacts/line-3/wall.png` (wall continuation), both identical 1254 × 1254
RGB PNGs. `dist/line-3/22.jpg` is a 512 × 512 RGB JPEG, under 100 KB. Record 22
uses the finished PNG's SHA-256. Existing records 01–21 remain unchanged.

The added bowl holds received pebbles: Pepe counts what reaches the bowl before
trusting a payment. A worn pigment addition occupies only x=709–1061,
y=350–587. All other pixels, the existing Pepe and the three-stone chain are
unchanged. Rock, cracks, framing, dimensions and light remain inherited.
The chosen review step was opening and visually inspecting the complete final
wall after compositing. Pepe retains his wide mouth and heavy-lidded eyes;
the new mark uses red/yellow ochre and charcoal, flattened rather than shaded
as a rendered object. No hands or handprints are added; the ancestor's hands
are hidden, so there are zero visible hands whose digits need counting. No
letters, numbers, captions, signatures, logos, frames, real people or prohibited
symbols were observed. No unmet visual requirements were observed. This is a
local review, not independent visual certification. Machine-readable dimensions,
formats and preservation results are in `wall-review-22.json`.

The installed assignment image tool (`mcp__image__generate`) was used under the
imagegen workflow. Its final prompt requested a single sparse prehistoric bowl
of ochre pebbles on pure white, irregular worn burnt-stick lines, red/yellow
ochre and charcoal only, no text, signatures, hands, modern symbols or frames.
Only its pigment mask was laid onto the original wall; no intermediate picture
remains in the delivery.

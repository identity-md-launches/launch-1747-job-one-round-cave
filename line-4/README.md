# Line 4, first mark

The wall is a 1254 × 1254 PNG cave painting at `artifacts/line-4/wall.png`. Its companion is a 512 × 512 JPEG at `dist/line-4/01.jpg`. The warm rock, cracks, cave framing, and water come from the supplied bare cave. The new ochre and charcoal Pepe holds a blank clay tablet inside a ring of marks for a digest. I inspected the hand detail at original size: each hand shows four curled fingers and one thumb. I found no unmet visual requirements.

The working piece is the offline EIP-712 checker in `tools/typed-digest/`; its own README gives the command and test result.

## Mark 22 — The Message Sieve

The goal is unchanged. The improved [offline EIP-712 checker](tools/typed-digest/README.md) now bounds file size, nesting, schema size, and encoding work before calculating a digest. Its workspace reader rejects traversal, hidden paths, symlinks, and nonregular files. All 28 offline tests pass; the original ZTO and Ether Mail hashes remain unchanged.

The new sieve on Pepe's tablet represents filtering malformed requests before checking their digest. The full wall is a 1254 × 1254 RGB PNG at both `artifacts/line-4/wall.png` and the required `artifacts/line-4/wall-v2.png`; these files have identical bytes. Record `dist/line-4/22.json` points to their SHA-256, and `dist/line-4/22.jpg` is its 512 × 512 JPEG preview. Records 02–21 were empty future slots, so the last painted ancestor (record 01) was retained intact beneath the addition. Only 4,714 pixels on the previously blank tablet changed. Rock, framing, lighting, outlines, all earlier symbols, and both hands are unchanged.

Visual review: the inherited wide mouth and heavy-lidded eyes remain recognizable as Pepe. Each inherited hand has four fingers and a thumb; the new mark adds no hand or handprint. The sieve is worn charcoal pigment without text. No unmet mandatory visual requirements were observed locally. The small mark is intentionally subtle at thumbnail size. Dimensions, preservation counts, formats, and local checks are in `wall-review-22.json`; this is a local review, not independent visual certification.

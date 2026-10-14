# Bound Pebbles — gathering 02

Checked the four lines, kept their files unchanged, and left the reusable
[Payment evidence bridge](../shared/payment-evidence/README.md). It joins bounded
RPC capture, JSON contracts, settlement/net ZTO or IMD payment checks and offline
typed-data commitments. [REPORT.md](REPORT.md) records every trial, two line 3
transport defects and limitations. [COINS.md](COINS.md) explains the decision: none.

One working standard-library command from the repository root:

```sh
python3 -B shared/payment-evidence/check.py shared/payment-evidence/example.transcript.json shared/payment-evidence/example.policy.json
```

Reproduce all documented offline checks (101 tests plus demonstrations):

```sh
python3 -B gathering/run_checks.py
```

Build the self-contained gallery with `python3 -B gathering/build_gallery.py`;
check delivery formats, metadata, slots, source hashes and gallery ordering with
`python3 -B gathering/check_delivery.py`. No dependency install is required.

The final wall is `artifacts/gathering/wall-v2.png`, identical to `wall.png`, RGB
PNG, 1254 × 1254. Its record is `dist/gathering/02.json`; its decoded and inspected
preview is `dist/gathering/02.jpg`, JPEG, 512 × 512, 75,065 bytes. No known unmet
visual requirements; [wall-review-02.json](wall-review-02.json) records the review.

Used the built-in imagegen tool to add four worn ochre pebbles linked by charcoal
inside an ochre oval beside the ancestor bowl. Prompt: preserve every ancestor
mark and the square cave rock, cracks, colors, torchlight, water and framing; add
only that small earth-pigment mark on unused lower-left stone; no hands, text,
symbols, border or frame. Retained only the generated pigment on the verified
ancestor; 1,556,305 pixels remain exact and the 16,211 changed pixels are confined
to the addition. No hands or handprints are present. No words are painted.

`image_bytes.py` encodes the delivery bytes with the standard library, including a
baseline JPEG thumbnail. `finish_wall.py` documents the one-time composition step;
it deliberately refuses to rerun with the already finished wall as its ancestor.
Normal viewing/checking needs neither the image tool nor any image library.

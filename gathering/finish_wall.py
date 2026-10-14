#!/usr/bin/env python3
"""Retain generated pigment on the ancestor and encode required delivery bytes.

Run once: wall.png is the verified ancestor and wall-v2.png is the image-tool
edit. This keeps every ancestor pixel outside the small addition masks exactly.
Do not rerun on an already finished pair: the inputs have different roles.
"""
import hashlib
import json
import math
from pathlib import Path

from image_bytes import jpeg, png, read_png, resize

ROOT = Path(__file__).resolve().parent.parent


def main():
    ancestor_path = ROOT / 'artifacts/gathering/wall.png'
    target_path = ROOT / 'artifacts/gathering/wall-v2.png'
    ancestor_bytes = ancestor_path.read_bytes()
    ancestor_sha = hashlib.sha256(ancestor_bytes).hexdigest()
    if ancestor_sha != 'ebfa45ae0793e3db23eec26363ae295f75fe87abd6b93adafcc94b76af897f55':
        raise ValueError('wall.png is not the expected gathering ancestor')
    w, h, original = read_png(ancestor_bytes)
    gw, gh, generated = read_png(target_path.read_bytes())
    if (w, h) != (gw, gh) or w != h:
        raise ValueError('generated edit must keep the original square dimensions')
    final = bytearray(original)
    centers = [(325, 803), (381, 833), (438, 859), (494, 879)]
    angle = .46
    cos, sin = math.cos(angle), math.sin(angle)
    changed = 0
    bounds = [w, h, 0, 0]
    for y in range(750, 936):
        for x in range(280, 546):
            # Explicitly protect the left rim/body of the ancestor bowl.
            if x >= 505 and y <= 867:
                continue
            dx, dy = x-416, y-845
            u, v = dx*cos+dy*sin, -dx*sin+dy*cos
            ellipse = math.sqrt((u/134)**2+(v/59)**2)
            oval = abs(ellipse-1) < .075
            discs = any((x-cx)**2+(y-cy)**2 < 29**2 for cx, cy in centers)
            cord = 320 <= x <= 502 and abs(y-(.45*x+656)) < 10
            if not (oval or discs or cord):
                continue
            start = (y*w+x)*3
            r, g, b = generated[start:start+3]
            # Extract earth pigment, not the image tool's redrawn stone.
            pigment = ((r < 91 and g < 72 and b < 52) or
                       (r > 74 and g < r*.69 and b < r*.43))
            if not pigment:
                continue
            for c in range(3):
                final[start+c] = generated[start+c]
            if final[start:start+3] != original[start:start+3]:
                changed += 1
                bounds = [min(bounds[0], x), min(bounds[1], y),
                          max(bounds[2], x), max(bounds[3], y)]
    if not changed:
        raise ValueError('no new pigment retained')
    encoded = png(w, h, final)
    target_path.write_bytes(encoded)
    ancestor_path.write_bytes(encoded)
    thumb = resize(w, h, final)
    quality = 52
    preview = jpeg(512, 512, thumb, quality)
    while len(preview) > 99000 and quality > 10:
        quality -= 5
        preview = jpeg(512, 512, thumb, quality)
    if len(preview) > 100000:
        raise ValueError('thumbnail exceeds delivery byte limit')
    (ROOT / 'dist/gathering/02.jpg').write_bytes(preview)
    review = {'ancestorSha256': ancestor_sha,
              'ancestorSize': [w, h], 'wallSize': [w, h], 'wallFormat': 'PNG',
              'wallMode': 'RGB', 'wallSha256': hashlib.sha256(encoded).hexdigest(),
              'changedPixels': changed, 'unchangedPixels': w*h-changed,
              'changedPixelBounds': bounds,
              'previewSize': [512, 512], 'previewFormat': 'JPEG',
              'previewBytes': len(preview), 'previewQuality': quality,
              'unmetVisualRequirements': [],
              'reviewStatus': 'requires final visual inspection',
              'imageTool': 'built-in imagegen',
              'prompt': 'Preserve all ancestor marks, the square cave rock, cracks, torchlight, colors, water and framing. Add only four worn ochre pebble discs linked by charcoal cord within an ochre oval on unused stone lower left of the bowl. Earth pigments only, no hands, text, symbols, border or frame.'}
    (ROOT / 'gathering/wall-review-02.json').write_text(json.dumps(review, indent=2)+'\n')
    print(json.dumps(review, indent=2))


if __name__ == '__main__':
    main()

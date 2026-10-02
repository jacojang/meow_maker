"""Compose PNGs on a neutral background into one contact sheet and report alpha stats.

Usage: uv run python contact_sheet.py out.png in1.png in2.png ... [--cols N] [--cell PX] [--bg R,G,B]
"""

import argparse
from pathlib import Path

from PIL import Image


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("out", type=Path)
    parser.add_argument("inputs", nargs="+", type=Path)
    parser.add_argument("--cols", type=int, default=3)
    parser.add_argument("--cell", type=int, default=420)
    parser.add_argument("--bg", default="150,150,160")
    args = parser.parse_args()

    bg = tuple(int(v) for v in args.bg.split(",")) + (255,)
    rows = -(-len(args.inputs) // args.cols)
    sheet = Image.new("RGBA", (args.cell * args.cols, args.cell * rows), bg)
    for index, path in enumerate(args.inputs):
        image = Image.open(path).convert("RGBA")
        alpha = image.getchannel("A")
        corners = [alpha.getpixel(p) for p in [(0, 0), (image.width - 1, 0), (0, image.height - 1), (image.width - 1, image.height - 1)]]
        bbox = alpha.point(lambda v: 255 if v > 20 else 0).getbbox()
        solid = sum(1 for v in alpha.getdata() if v > 20)
        semi = sum(1 for v in alpha.getdata() if 20 < v < 235)
        semi_ratio = semi / solid if solid else 0.0
        print(f"{path.name}: {image.size} corners={corners} bbox={bbox} semi_transparent={semi_ratio:.3f}")
        tile = image.resize((args.cell, args.cell))
        sheet.alpha_composite(tile, (args.cell * (index % args.cols), args.cell * (index // args.cols)))
    sheet.convert("RGB").save(args.out)


if __name__ == "__main__":
    main()

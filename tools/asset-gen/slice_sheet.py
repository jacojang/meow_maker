"""Slice a framed animation sheet into its panels by detecting the dark panel borders.

Usage: uv run python slice_sheet.py sheet.png out_prefix [--size 512] [--expect 5]
Writes out_prefix-1.png ... in reading order (left to right, top to bottom); reports panel boxes.
"""

import argparse
from pathlib import Path

import numpy as np
from PIL import Image

DARK = 90
CREAM = (246, 235, 217)


def long_runs(mask: np.ndarray, axis: int, min_len: int) -> list[int]:
    """Indices (rows if axis=1, columns if axis=0) holding a dark run of at least min_len."""
    hits = []
    lines = mask if axis == 1 else mask.T
    for index, line in enumerate(lines):
        run = best = 0
        for value in line:
            run = run + 1 if value else 0
            best = max(best, run)
        if best >= min_len:
            hits.append(index)
    return hits


def cluster(indices: list[int], gap: int = 4) -> list[tuple[int, int]]:
    groups: list[list[int]] = []
    for value in indices:
        if groups and value - groups[-1][-1] <= gap:
            groups[-1].append(value)
        else:
            groups.append([value])
    return [(g[0], g[-1]) for g in groups]


def find_panels(gray: np.ndarray) -> list[tuple[int, int, int, int]]:
    mask = gray < DARK
    height, width = mask.shape
    row_lines = cluster(long_runs(mask, 1, int(width * 0.18)))
    panels = []
    row_bands = [(a[1], b[0], a[0], b[1]) for a, b in zip(row_lines, row_lines[1:]) if b[0] - a[1] > height * 0.25]
    for _, _, top, bottom in row_bands:
        band = mask[top : bottom + 1]
        col_lines = cluster(long_runs(band, 0, int((bottom - top) * 0.6)))
        for a, b in zip(col_lines, col_lines[1:]):
            if b[0] - a[1] > width * 0.12:
                panels.append((a[0], top, b[1], bottom))
    return panels


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("sheet", type=Path)
    parser.add_argument("prefix")
    parser.add_argument("--size", type=int, default=512)
    parser.add_argument("--expect", type=int, default=5)
    args = parser.parse_args()

    image = Image.open(args.sheet).convert("RGB")
    gray = np.asarray(image.convert("L"))
    panels = find_panels(gray)
    print(f"{args.sheet.name}: {len(panels)} panels")
    for index, (x0, y0, x1, y1) in enumerate(panels, 1):
        print(f"  {index}: x={x0}-{x1} y={y0}-{y1} size={x1 - x0 + 1}x{y1 - y0 + 1}")
    if len(panels) < args.expect:
        raise SystemExit(f"expected at least {args.expect} panels")
    for index, box in enumerate(panels[: args.expect], 1):
        crop = image.crop((box[0], box[1], box[2] + 1, box[3] + 1))
        scale = args.size / max(crop.size)
        crop = crop.resize((round(crop.width * scale), round(crop.height * scale)), Image.LANCZOS)
        square = Image.new("RGB", (args.size, args.size), CREAM)
        square.paste(crop, ((args.size - crop.width) // 2, (args.size - crop.height) // 2))
        square.save(f"{args.prefix}-{index}.png")


if __name__ == "__main__":
    main()

"""Measure the shipped cat portraits and write the metrics JSON the game reads.

Zero image-generation calls. Usage (from tools/asset-gen):
    uv run python measure_portraits.py [--check]
--check exits non-zero if the committed metrics are stale instead of writing.
"""
import argparse
import hashlib
import json
import sys
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[2]
CATS_DIR = ROOT / "web" / "public" / "assets" / "cats"
METRICS_PATH = ROOT / "web" / "src" / "data" / "catMetrics.json"
ALPHA_THRESHOLD = 20
PREFIX = "cat-"


def measure(path: Path) -> dict:
    image = Image.open(path).convert("RGBA")
    mask = image.getchannel("A").point(lambda a: 255 if a > ALPHA_THRESHOLD else 0)
    bbox = mask.getbbox()
    if bbox is None:
        raise ValueError(f"{path.name}: no opaque pixels")
    left, top, right, bottom = bbox
    return {
        "file": path.name,
        "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
        "width": image.width,
        "height": image.height,
        "bbox": {"left": left, "top": top, "right": right, "bottom": bottom},
        "bboxHeight": bottom - top,
        "bboxWidth": right - left,
        "bboxCenterX": (left + right) / 2,
        "floorY": bottom,
    }


def build_metrics(cats_dir: Path = CATS_DIR) -> dict:
    cats = {}
    for path in sorted(cats_dir.glob(f"{PREFIX}*.png")):
        cats[path.stem[len(PREFIX):]] = measure(path)
    return {"alphaThreshold": ALPHA_THRESHOLD, "cats": cats}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    text = json.dumps(build_metrics(), indent=2) + "\n"
    if args.check:
        current = METRICS_PATH.read_text() if METRICS_PATH.exists() else ""
        if current != text:
            print("metrics are stale; rerun without --check", file=sys.stderr)
            return 1
        return 0
    METRICS_PATH.parent.mkdir(parents=True, exist_ok=True)
    METRICS_PATH.write_text(text)
    print(f"wrote {METRICS_PATH}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

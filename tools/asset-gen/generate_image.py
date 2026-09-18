"""Generate a composited game art asset via the OpenAI Images API.

Dev-time tool only — not called by the running game. See
docs/development/README.md for setup and docs/planning/opening-screen.md
for why this exists.

Usage:
    uv run python generate_image.py --prompt "..." --ref a.png --ref b.png --out out.png
"""

import argparse
import base64
import sys
from contextlib import ExitStack
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI

VALID_SIZES = {"1024x1024", "1024x1536", "1536x1024", "auto"}
VALID_BACKGROUNDS = {"auto", "opaque", "transparent"}
VALID_QUALITIES = {"auto", "low", "medium", "high", "standard", "xhigh", "max"}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--prompt", required=True, help="What to generate")
    parser.add_argument(
        "--ref",
        action="append",
        dest="refs",
        default=[],
        help="Reference image path (repeatable) to compose/edit from",
    )
    parser.add_argument("--out", required=True, type=Path, help="Output PNG path")
    parser.add_argument("--size", default="1536x1024", choices=sorted(VALID_SIZES))
    parser.add_argument(
        "--background",
        default="auto",
        choices=sorted(VALID_BACKGROUNDS),
        help="'transparent' requires PNG output (the default --out extension)",
    )
    parser.add_argument("--model", default="gpt-image-1", help="Image model to use")
    parser.add_argument("--quality", default="auto", choices=sorted(VALID_QUALITIES))
    return parser.parse_args()


def main() -> None:
    load_dotenv()
    args = parse_args()

    for ref in args.refs:
        if not Path(ref).is_file():
            sys.exit(f"Reference image not found: {ref}")

    client = OpenAI()  # reads OPENAI_API_KEY from the environment

    with ExitStack() as stack:
        if args.refs:
            files = [stack.enter_context(open(ref, "rb")) for ref in args.refs]
            result = client.images.edit(
                model=args.model,
                image=files,
                prompt=args.prompt,
                size=args.size,
                background=args.background,
                quality=args.quality,
            )
        else:
            result = client.images.generate(
                model=args.model,
                prompt=args.prompt,
                size=args.size,
                background=args.background,
                quality=args.quality,
            )

    image_bytes = base64.b64decode(result.data[0].b64_json)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_bytes(image_bytes)
    print(f"Wrote {args.out} ({len(image_bytes)} bytes)")


if __name__ == "__main__":
    main()

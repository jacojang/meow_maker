"""Run asset-gen jobs sequentially with retry on rate limits; skip outputs that already exist.

Usage: uv run python batch_generate.py jobs.json
jobs.json: [{"out": "...", "prompt_cmd": ["./portrait_prompt.sh", ...], "refs": [...],
             "background": "transparent|opaque", "quality": "medium", "size": "1024x1024"}]
"""

import json
import subprocess
import sys
import time
from pathlib import Path


def run_job(job: dict) -> bool:
    out = Path(job["out"])
    if out.exists():
        print(f"skip {out}")
        return True
    prompt = subprocess.run(job["prompt_cmd"], capture_output=True, text=True, check=True).stdout.strip()
    cmd = [
        "uv", "run", "python", "generate_image.py", "--prompt", prompt,
        "--size", job.get("size", "1024x1024"), "--background", job["background"],
        "--quality", job.get("quality", "medium"), "--model", "gpt-image-1-mini", "--out", str(out),
    ]
    for ref in job["refs"]:
        cmd += ["--ref", ref]
    for attempt in range(1, 6):
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode == 0:
            print(result.stdout.strip().splitlines()[-1])
            time.sleep(max(0, 12 * len(job["refs"]) - 6))
            return True
        print(f"retry {attempt} for {out}: {result.stderr.strip().splitlines()[-1][:120]}")
        time.sleep(20)
    return False


def main() -> None:
    jobs = json.loads(Path(sys.argv[1]).read_text())
    failed = [job["out"] for job in jobs if not run_job(job)]
    print("FAILED:" if failed else "ALL DONE", *failed)
    if failed:
        sys.exit(1)


if __name__ == "__main__":
    main()

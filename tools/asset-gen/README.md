# asset-gen

A dev-time tool, not part of the shipped game. It calls the OpenAI Images
API (`gpt-image-1`) to composite reference art (character sheets, background
photos) into a single illustration, since no image-generation capability
exists in this repo's normal workflow otherwise. Output PNGs get committed
as game assets under `web/`; the tool itself doesn't run in production.

## Setup

1. Get an API key at <https://platform.openai.com/api-keys>.
2. Copy `.env.example` (repo root) to `.env` and fill in `OPENAI_API_KEY`.
   `.env` is gitignored — never commit it.
3. `cd tools/asset-gen && uv sync`

## Usage

```
uv run python generate_image.py \
  --prompt "Describe the scene to generate" \
  --ref path/to/reference1.png \
  --ref path/to/reference2.png \
  --out path/to/output.png
```

- `--ref` is repeatable; pass 0+ reference images. With no `--ref`, it
  generates from the prompt alone. With one or more, it uses the Images
  *edit* endpoint to compose/blend them per the prompt.
- `--size` defaults to `1536x1024`; other options are `1024x1024`,
  `1024x1536`, `auto`.
- Costs real money per call — check the prompt before running, and prefer
  fewer, more deliberate iterations over rapid trial-and-error.

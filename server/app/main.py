from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

WEB_DIST_DIR = Path(__file__).resolve().parent.parent.parent / "web" / "dist"

app = FastAPI()


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


app.mount("/", StaticFiles(directory=WEB_DIST_DIR, html=True), name="static")

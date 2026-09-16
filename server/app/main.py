from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from .api import router as api_router
from .session import issue_session_cookie

WEB_DIST_DIR = Path(__file__).resolve().parent.parent.parent / "web" / "dist"

app = FastAPI()


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


app.include_router(api_router)

app.middleware("http")(issue_session_cookie)

app.mount("/", StaticFiles(directory=WEB_DIST_DIR, html=True), name="static")

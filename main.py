"""Embarko entrypoint – re-exports the FastAPI app from apps.api.main."""
import os, sys

# Ensure project root is on the path so `apps.api` / `packages` resolve
sys.path.insert(0, os.path.dirname(__file__))

from apps.api.main import app  # noqa: F401 – Embarko / uvicorn discovers `app`

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.environ.get("PORT", 8000)))


"""Application entrypoint.

Creates the FastAPI application, enables CORS for the Vite dev server, and
wires up the routes from :mod:`game2048.api`.

Run locally with::

    uv run uvicorn game2048.main:app --reload
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from game2048.api import router

# Origins allowed to call the API from a browser. The Vite dev server serves
# the frontend at :5173 by default; add deployed origins here as needed.
ALLOWED_ORIGINS = [
    'http://localhost:5173',
    'http://127.0.0.1:5173',
]

app = FastAPI(title='2048', version='0.1.0')

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_methods=['*'],
    allow_headers=['*'],
)

app.include_router(router)


@app.get('/health')
def health() -> dict[str, str]:
    """Simple liveness probe."""
    return {'status': 'ok'}

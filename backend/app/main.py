from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .core.config import settings
from .api.routes.predictions import router as predictions_router
from .api.routes.riot import router as riot_router

app = FastAPI(title="DraftDiff API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_allow_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/v1/health")
async def health() -> dict:
    return {"status": "ok", "version": app.version}


app.include_router(predictions_router, prefix="/api/v1")
app.include_router(riot_router, prefix="/api/v1")

import os
import time
import logging
from typing import Optional

from fastapi import FastAPI, HTTPException, Header, Request
from fastapi.responses import JSONResponse

from app.schemas import PredictRequest, PredictResponse
from app.registry import load_model

logging.basicConfig(level=os.getenv("LOG_LEVEL", "info").upper())
log = logging.getLogger("gcinside.ai")

app = FastAPI(title="gcinside-ai-inference", version="0.1.0")

_MODEL = load_model()
_TOKEN = os.getenv("AI_INFERENCE_TOKEN", "")


@app.get("/health")
def health() -> dict:
    return {"status": "ok", "modelVersion": _MODEL.version}


@app.middleware("http")
async def access_log(request: Request, call_next):
    started = time.perf_counter()
    response = await call_next(request)
    dur_ms = (time.perf_counter() - started) * 1000
    log.info("%s %s -> %s in %.1fms", request.method, request.url.path, response.status_code, dur_ms)
    return response


def _check_auth(authorization: Optional[str]) -> None:
    if not _TOKEN:
        return
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="unauthorized")
    presented = authorization[len("Bearer "):].strip()
    if presented != _TOKEN:
        raise HTTPException(status_code=401, detail="unauthorized")


@app.post("/v1/predict-risk", response_model=PredictResponse)
def predict_risk(req: PredictRequest, authorization: Optional[str] = Header(default=None)) -> PredictResponse:
    _check_auth(authorization)
    return _MODEL.predict(req)


@app.exception_handler(Exception)
async def on_unhandled(_request: Request, exc: Exception):
    log.exception("unhandled error", exc_info=exc)
    return JSONResponse(status_code=500, content={"error": "internal_error"})

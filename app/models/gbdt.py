"""Pickle-backed GBDT risk model produced by gcinside-ml-pipeline."""

from __future__ import annotations

import pickle
from pathlib import Path
from typing import Any

from app.models.base import RiskModel
from app.schemas import PredictRequest, PredictResponse


ARTIFACT_KIND = "gcinside-risk-gbdt"


def _clamp01(x: float) -> float:
    return max(0.0, min(1.0, x))


def _feature_dict(req: PredictRequest) -> dict[str, str | float | bool]:
    f = req.features
    return {
        "action": req.action,
        "request_count_1m": f.requestCount1m,
        "request_count_10m": f.requestCount10m,
        "account_age_minutes": f.accountAgeMinutes,
        "typing_interval_avg": f.typingIntervalAvg,
        "typing_interval_variance": f.typingIntervalVariance,
        "paste_used": f.pasteUsed,
        "submit_elapsed_ms": f.submitElapsedMs,
        "reputation_score": f.reputationScore,
        "content_similarity_count": f.contentSimilarityCount,
    }


def _reasons(score: float) -> list[str]:
    if score >= 0.85:
        return ["gbdt_very_high_risk"]
    if score >= 0.65:
        return ["gbdt_high_risk"]
    if score >= 0.45:
        return ["gbdt_medium_risk"]
    return []


class GBDTRiskModel(RiskModel):
    def __init__(self, artifact_path: str | Path, version_override: str | None = None) -> None:
        with open(artifact_path, "rb") as f:
            artifact: dict[str, Any] = pickle.load(f)
        if artifact.get("kind") != ARTIFACT_KIND:
            raise ValueError(f"unsupported artifact kind: {artifact.get('kind')}")
        self._artifact = artifact
        self._model = artifact["model"]
        self._version = version_override or str(artifact.get("version") or "risk-gbdt")

    @property
    def version(self) -> str:
        return self._version

    def predict(self, req: PredictRequest) -> PredictResponse:
        score = float(self._model.predict_proba([_feature_dict(req)])[0][1])
        score = _clamp01(score)
        return PredictResponse(
            mlScore=score,
            modelVersion=req.modelVersion or self.version,
            reasons=_reasons(score),
        )

from app.models.base import RiskModel
from app.schemas import PredictRequest, PredictResponse


def _clamp01(x: float) -> float:
    return max(0.0, min(1.0, x))


class MockRiskModel(RiskModel):
    """Deterministic baseline. Always replaceable, never random."""

    def __init__(self, version: str = "mock-risk-v1") -> None:
        self._version = version

    @property
    def version(self) -> str:
        return self._version

    def predict(self, req: PredictRequest) -> PredictResponse:
        f = req.features
        reasons: list[str] = []
        score = 0.0

        if f.requestCount1m >= 60:
            score += 0.45
            reasons.append("burst_requests_60")
        elif f.requestCount1m >= 30:
            score += 0.25
            reasons.append("burst_requests_30")

        if f.requestCount10m >= 200:
            score += 0.15
            reasons.append("sustained_volume")

        if f.accountAgeMinutes and f.accountAgeMinutes < 60 and f.requestCount10m >= 20:
            score += 0.25
            reasons.append("new_account_burst")

        if f.submitElapsedMs and f.submitElapsedMs < 300:
            score += 0.25
            reasons.append("submit_too_fast")

        if f.pasteUsed and f.typingIntervalAvg < 1.0:
            score += 0.15
            reasons.append("paste_no_typing")

        if 0 < f.typingIntervalVariance < 0.001 and f.requestCount1m > 0:
            score += 0.1
            reasons.append("typing_too_uniform")

        if f.contentSimilarityCount >= 5:
            score += 0.2
            reasons.append("duplicate_content")
        elif f.contentSimilarityCount >= 2:
            score += 0.1
            reasons.append("near_duplicate_content")

        # Reputation modifier (high reputation pulls score down)
        score -= 0.1 * max(0.0, f.reputationScore - 0.5) * 2.0

        return PredictResponse(
            mlScore=_clamp01(score),
            modelVersion=req.modelVersion or self.version,
            reasons=reasons,
        )

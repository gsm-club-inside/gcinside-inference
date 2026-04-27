from typing import Optional
from pydantic import BaseModel, Field, field_validator


class Subject(BaseModel):
    userId: Optional[str] = None
    sessionId: Optional[str] = None
    ipHash: Optional[str] = None
    deviceHash: Optional[str] = None


class Features(BaseModel):
    requestCount1m: float = 0
    requestCount10m: float = 0
    accountAgeMinutes: float = 0
    typingIntervalAvg: float = 0
    typingIntervalVariance: float = 0
    pasteUsed: bool = False
    submitElapsedMs: float = 0
    reputationScore: float = 0
    contentSimilarityCount: float = 0


class PredictRequest(BaseModel):
    requestId: str = Field(..., min_length=1, max_length=128)
    action: str = Field(..., min_length=1, max_length=64)
    subject: Subject = Field(default_factory=Subject)
    features: Features = Field(default_factory=Features)

    @field_validator("action")
    @classmethod
    def _action(cls, v: str) -> str:
        allowed = {
            "sign_up",
            "sign_in",
            "create_post",
            "create_comment",
            "vote",
            "search",
            "upload",
            "report",
        }
        if v not in allowed:
            raise ValueError(f"unknown action: {v}")
        return v


class PredictResponse(BaseModel):
    mlScore: float
    modelVersion: str
    reasons: list[str]

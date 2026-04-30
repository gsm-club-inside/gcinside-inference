"""Model registry placeholder.

Future:
  - load model artifact from Object Storage by `MODEL_PATH`
  - support shadow / canary / rollback via env
  - hot-reload signal
"""
import os
from app.models.base import RiskModel
from app.models.gbdt import GBDTRiskModel
from app.models.mock import MockRiskModel


def load_model() -> RiskModel:
    name = os.getenv("MODEL_NAME", "mock-risk-v1")
    model_path = os.getenv("MODEL_PATH", "").strip()
    if model_path:
        return GBDTRiskModel(model_path, version_override=name if name != "mock-risk-v1" else None)
    return MockRiskModel(version=name)

"""Model registry placeholder.

Future:
  - load model artifact from Object Storage by `MODEL_PATH`
  - support shadow / canary / rollback via env
  - hot-reload signal
"""
import os
from app.models.base import RiskModel
from app.models.mock import MockRiskModel


def load_model() -> RiskModel:
    name = os.getenv("MODEL_NAME", "mock-risk-v1")
    # MODEL_PATH would point to an artifact bucket key. Wire LightGBM/XGBoost here later.
    return MockRiskModel(version=name)

from abc import ABC, abstractmethod
from app.schemas import PredictRequest, PredictResponse


class RiskModel(ABC):
    """Pluggable risk model. Replace MockRiskModel with LightGBM / XGBoost / IsolationForest etc."""

    @property
    @abstractmethod
    def version(self) -> str: ...

    @abstractmethod
    def predict(self, req: PredictRequest) -> PredictResponse: ...

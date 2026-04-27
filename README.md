# gcinside-ai-inference

GCinside risk score 추론 전용 서비스. `gcinside-app` 의 anti-abuse 도메인이 HTTP 로 호출합니다.

## 역할

- `GET /health`
- `POST /v1/predict-risk` — request features → `mlScore`, `modelVersion`, `reasons`
- 초기엔 deterministic mock model (`mock-risk-v1`).
- `app/models/base.py` 의 `RiskModel` interface 만 구현하면 LightGBM / XGBoost / IsolationForest / sequence model 등으로 교체 가능.

## 실행

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements-dev.txt
uvicorn app.main:app --host 0.0.0.0 --port 8081
```

또는

```bash
docker build -t gcinside-ai-inference .
docker run --rm -p 8081:8081 -e AI_INFERENCE_TOKEN=secret gcinside-ai-inference
```

## API

```
POST /v1/predict-risk
Authorization: Bearer <AI_INFERENCE_TOKEN>   # token 미설정 시 인증 생략
Content-Type: application/json

{
  "requestId": "req-1",
  "action": "create_post",
  "subject": { "userId": "1", "sessionId": null, "ipHash": null, "deviceHash": null },
  "features": {
    "requestCount1m": 0,
    "requestCount10m": 0,
    "accountAgeMinutes": 0,
    "typingIntervalAvg": 0,
    "typingIntervalVariance": 0,
    "pasteUsed": false,
    "submitElapsedMs": 0,
    "reputationScore": 0,
    "contentSimilarityCount": 0
  }
}
```

응답:

```json
{
  "mlScore": 0.72,
  "modelVersion": "mock-risk-v1",
  "reasons": ["burst_requests_60", "submit_too_fast"]
}
```

## 환경변수

| 변수 | 설명 | 기본값 |
|---|---|---|
| `PORT` | 서비스 포트 | 8081 |
| `HOST` | 바인딩 호스트 | 0.0.0.0 |
| `MODEL_NAME` | `modelVersion` 응답값 | `mock-risk-v1` |
| `MODEL_PATH` | (placeholder) Object Storage artifact key | (없음) |
| `AI_INFERENCE_TOKEN` | Bearer 토큰. 비우면 인증 생략 | (없음) |
| `LOG_LEVEL` | uvicorn / app 로그 레벨 | `info` |

## 검증

```bash
pip install -r requirements-dev.txt
pytest
ruff check app
```

## 운영 메모

- 메인 앱(`gcinside-app`) 의 client 는 짧은 timeout (기본 250ms) + 1 retry 로 호출하고, 실패하면 rule 기반 fallback 합니다. AI 장애가 메인 서비스 장애로 번지지 않도록 설계되어 있습니다.
- 입력은 **이미 hash 된 식별자**만 받습니다. 원문 IP / device 식별자를 받지 마세요.
- 모델 교체 시 `MODEL_NAME` 변경으로 메인 앱 audit 의 `modelVersion` 이 즉시 반영됩니다.

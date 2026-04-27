from fastapi.testclient import TestClient
from app.main import app


def test_health():
    c = TestClient(app)
    r = c.get("/health")
    assert r.status_code == 200
    body = r.json()
    assert body["status"] == "ok"
    assert "modelVersion" in body


def test_predict_low_risk():
    c = TestClient(app)
    r = c.post(
        "/v1/predict-risk",
        json={
            "requestId": "req-1",
            "action": "vote",
            "subject": {"userId": "1"},
            "features": {
                "requestCount1m": 1,
                "requestCount10m": 5,
                "accountAgeMinutes": 60_000,
                "typingIntervalAvg": 200,
                "typingIntervalVariance": 100,
                "pasteUsed": False,
                "submitElapsedMs": 5000,
                "reputationScore": 0.8,
                "contentSimilarityCount": 0,
            },
        },
    )
    assert r.status_code == 200
    body = r.json()
    assert 0 <= body["mlScore"] <= 1
    assert body["modelVersion"]
    assert body["mlScore"] < 0.3


def test_predict_high_risk():
    c = TestClient(app)
    r = c.post(
        "/v1/predict-risk",
        json={
            "requestId": "req-2",
            "action": "create_post",
            "subject": {"sessionId": "s"},
            "features": {
                "requestCount1m": 90,
                "requestCount10m": 250,
                "accountAgeMinutes": 5,
                "typingIntervalAvg": 0,
                "typingIntervalVariance": 0,
                "pasteUsed": True,
                "submitElapsedMs": 80,
                "reputationScore": 0.1,
                "contentSimilarityCount": 6,
            },
        },
    )
    assert r.status_code == 200
    body = r.json()
    assert body["mlScore"] > 0.5
    assert "burst_requests_60" in body["reasons"]


def test_predict_unknown_action():
    c = TestClient(app)
    r = c.post(
        "/v1/predict-risk",
        json={"requestId": "x", "action": "nope", "subject": {}, "features": {}},
    )
    assert r.status_code == 422

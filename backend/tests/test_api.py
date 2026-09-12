from app.core.config import RuleConfig
from app.core.enums import FraudType
from app.fraud.engine import persist_case
from app.fraud.types import Signal
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session


def create_case(session: Session, signal: Signal) -> int:
    case, _ = persist_case(session, 1, [signal], RuleConfig())
    session.commit()
    return case.id


def test_api_full_review_flow_and_original_evidence(
    client: TestClient, session: Session, signal: Signal
) -> None:
    case_id = create_case(session, signal)
    assert client.get("/health").status_code == 200
    assert client.get("/drivers").json()[0]["external_driver_id"] == "D001"
    assert client.get("/drivers/1").json()["created_at"].endswith("Z")
    case = client.get(f"/fraud-cases/{case_id}").json()
    assert case["score_breakdown"] == {"gps_spoofing": 30}
    evidence = client.get(f"/fraud-cases/{case_id}/evidence").json()[0]
    original = client.get(f"/fraud-cases/{case_id}/evidence/{evidence['id']}/sources").json()[0]
    assert original["source_type"] == "trip"
    assert original["data"]["driver_id"] == 1
    assert original["data"]["pickup_lat"] == 10.77
    review = {"reviewer": "control_user_01", "reason": "Inspecting GPS records"}
    assert client.post(f"/fraud-cases/{case_id}/review", json=review).status_code == 200
    assert (
        client.post(f"/fraud-cases/{case_id}/request-explanation", json=review).status_code == 200
    )
    response = client.post(f"/fraud-cases/{case_id}/explanation", json={"explanation": "GPS loss"})
    assert response.status_code == 201
    assert response.json()["attachment_metadata"] == []
    decision = {"decision": "dismissed", **review}
    assert client.post(f"/fraud-cases/{case_id}/decision", json=decision).status_code == 201
    assert client.get(f"/fraud-cases/{case_id}").json()["status"] == "dismissed"
    assert client.get("/drivers/1").json()["status"] == "active"
    assert client.post(f"/fraud-cases/{case_id}/review", json=review).status_code == 409
    assert client.post(f"/fraud-cases/{case_id}/decision", json=decision).status_code == 409


def test_case_filters_include_secondary_category(
    client: TestClient, session: Session, signal: Signal
) -> None:
    promo = signal.model_copy(update={"fraud_type": FraudType.PROMOTION_ABUSE})
    case, _ = persist_case(session, 1, [signal, promo], RuleConfig())
    session.commit()
    assert case.fraud_type == FraudType.GPS_SPOOFING
    result = client.get(
        "/fraud-cases",
        params={
            "fraud_type": "promotion_abuse",
            "min_risk_score": 50,
            "driver_id": 1,
            "status": "detected",
        },
    )
    assert result.status_code == 200
    assert len(result.json()) == 1
    assert client.get("/fraud-cases?min_risk_score=51").json() == []
    assert client.get("/fraud-cases?driver_id=2").json() == []
    assert client.get("/fraud-cases?status=dismissed").json() == []
    assert client.get("/fraud-cases?limit=1&offset=1").json() == []


def test_api_rejects_invalid_inputs_and_state_changes(
    client: TestClient, session: Session, signal: Signal
) -> None:
    case_id = create_case(session, signal)
    for path in (
        "/drivers?limit=0",
        "/drivers?offset=-1",
        "/fraud-cases?min_risk_score=101",
        "/fraud-cases?status=unknown",
        "/fraud-cases?fraud_type=unknown",
        "/drivers/0",
    ):
        assert client.get(path).status_code == 422
    for path in (
        "/drivers/999",
        "/fraud-cases/999",
        "/fraud-cases/999/evidence",
        f"/fraud-cases/{case_id}/evidence/999/sources",
    ):
        assert client.get(path).status_code == 404
    decision = {"decision": "confirmed_fraud", "reviewer": "reviewer", "reason": "Reviewed"}
    assert client.post(f"/fraud-cases/{case_id}/decision", json=decision).status_code == 409
    assert (
        client.post(
            f"/fraud-cases/{case_id}/explanation", json={"explanation": "Too early"}
        ).status_code
        == 409
    )
    for patch in (
        {"reviewer": "   "},
        {"reason": " "},
        {"decision": "detected"},
        {"unexpected": "field"},
    ):
        assert (
            client.post(f"/fraud-cases/{case_id}/decision", json=decision | patch).status_code
            == 422
        )
    assert (
        client.post(f"/fraud-cases/{case_id}/explanation", json={"explanation": " "}).status_code
        == 422
    )


def test_confirmed_fraud_is_a_human_case_decision_only(
    client: TestClient, session: Session, signal: Signal
) -> None:
    case_id = create_case(session, signal)
    reviewer = {"reviewer": "control_user_01", "reason": "Original records verified"}
    client.post(f"/fraud-cases/{case_id}/review", json=reviewer)
    result = client.post(
        f"/fraud-cases/{case_id}/decision", json={"decision": "confirmed_fraud", **reviewer}
    )
    assert result.status_code == 201
    assert client.get("/drivers/1").json()["status"] == "active"

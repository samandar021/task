import time

import pytest

pytestmark = pytest.mark.unit


def test_health_returns_healthy(client) -> None:
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}


def test_get_message_existing_id(client) -> None:
    response = client.get("/message/1")

    assert response.status_code == 200
    assert response.json() == {"id": 1, "text": "Mock message #1"}


def test_get_message_missing_id_returns_404(client) -> None:
    response = client.get("/message/9999")

    assert response.status_code == 404
    assert response.json() == {"detail": "Message not found"}


def test_get_message_invalid_id_returns_422(client) -> None:
    response = client.get("/message/0")

    assert response.status_code == 422


def test_process_echo_and_latency_simulation(client) -> None:
    start = time.perf_counter()
    response = client.post("/process", json={"data": "hello"})
    elapsed = time.perf_counter() - start

    assert response.status_code == 200
    assert response.json() == {"processed": "hello"}
    assert elapsed >= 0.45


@pytest.mark.parametrize(
    "payload",
    [
        {"data": ""},
        {},
    ],
)
def test_process_validation_errors(client, payload: dict[str, str]) -> None:
    response = client.post("/process", json=payload)

    assert response.status_code == 422

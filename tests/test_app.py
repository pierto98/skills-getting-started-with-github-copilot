import pytest
from fastapi.testclient import TestClient

from src import app as app_module


@pytest.fixture
def sample_activities(monkeypatch):
    activities = {
        "Art Club": {
            "description": "Make art",
            "schedule": "Wednesdays",
            "max_participants": 10,
            "participants": ["member@example.com"],
        }
    }
    monkeypatch.setattr(app_module, "activities", activities)
    return activities


@pytest.fixture
def client(sample_activities):
    return TestClient(app_module.app, follow_redirects=False)


def test_root_redirects_to_static_index(client):
    response = client.get("/")

    assert response.status_code == 307
    assert response.headers["location"] == "/static/index.html"


def test_get_activities_returns_current_activities(client, sample_activities):
    response = client.get("/activities")

    assert response.status_code == 200
    assert response.json() == sample_activities


def test_signup_adds_participant(client, sample_activities):
    response = client.post(
        "/activities/Art Club/signup",
        params={"email": "new-member@example.com"},
    )

    assert response.status_code == 200
    assert response.json() == {
        "message": "Signed up new-member@example.com for Art Club"
    }
    assert "new-member@example.com" in sample_activities["Art Club"]["participants"]


def test_signup_returns_404_for_unknown_activity(client):
    response = client.post(
        "/activities/Unknown Club/signup",
        params={"email": "new-member@example.com"},
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_signup_returns_400_for_duplicate_participant(client):
    response = client.post(
        "/activities/Art Club/signup",
        params={"email": "member@example.com"},
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Student is already signed up for this activity"


def test_unregister_removes_participant(client, sample_activities):
    response = client.delete(
        "/activities/Art Club/signup",
        params={"email": "member@example.com"},
    )

    assert response.status_code == 200
    assert response.json() == {
        "message": "Unregistered member@example.com from Art Club"
    }
    assert sample_activities["Art Club"]["participants"] == []


def test_unregister_returns_404_for_unknown_activity(client):
    response = client.delete(
        "/activities/Unknown Club/signup",
        params={"email": "member@example.com"},
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_unregister_returns_404_for_unregistered_participant(client):
    response = client.delete(
        "/activities/Art Club/signup",
        params={"email": "missing@example.com"},
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Student is not signed up for this activity"
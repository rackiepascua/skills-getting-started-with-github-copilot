import copy

import pytest
from fastapi.testclient import TestClient

from src import app as app_module

client = TestClient(app_module.app)


@pytest.fixture(autouse=True)
def reset_activities():
    original_activities = copy.deepcopy(app_module.activities)
    yield
    app_module.activities = copy.deepcopy(original_activities)


def test_get_activities_returns_all_activities():
    # Arrange
    expected_activity_count = len(app_module.activities)

    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    assert len(data) == expected_activity_count
    assert "Chess Club" in data
    assert "Programming Class" in data


def test_signup_for_activity_adds_participant():
    # Arrange
    activity_name = "Chess Club"
    new_email = "newstudent@mergington.edu"
    initial_participants = list(app_module.activities[activity_name]["participants"])

    # Act
    response = client.post(
        f"/activities/{activity_name}/signup",
        params={"email": new_email},
    )

    # Assert
    assert response.status_code == 200
    result = response.json()
    assert "Signed up" in result["message"]
    assert new_email in app_module.activities[activity_name]["participants"]
    assert len(app_module.activities[activity_name]["participants"]) == len(initial_participants) + 1


def test_signup_for_activity_rejects_duplicate_registration():
    # Arrange
    activity_name = "Chess Club"
    existing_email = "michael@mergington.edu"
    initial_count = len(app_module.activities[activity_name]["participants"])

    # Act
    response = client.post(
        f"/activities/{activity_name}/signup",
        params={"email": existing_email},
    )

    # Assert
    assert response.status_code == 400
    result = response.json()
    assert result["detail"] == "Student already signed up"
    assert len(app_module.activities[activity_name]["participants"]) == initial_count


def test_remove_participant_removes_student():
    # Arrange
    activity_name = "Chess Club"
    participant_email = "daniel@mergington.edu"
    assert participant_email in app_module.activities[activity_name]["participants"]

    # Act
    response = client.delete(
        f"/activities/{activity_name}/participants",
        params={"email": participant_email},
    )

    # Assert
    assert response.status_code == 200
    result = response.json()
    assert "Removed" in result["message"]
    assert participant_email not in app_module.activities[activity_name]["participants"]


def test_remove_participant_returns_404_for_missing_student():
    # Arrange
    activity_name = "Chess Club"
    missing_email = "missing@mergington.edu"

    # Act
    response = client.delete(
        f"/activities/{activity_name}/participants",
        params={"email": missing_email},
    )

    # Assert
    assert response.status_code == 404
    result = response.json()
    assert result["detail"] == "Participant not found"

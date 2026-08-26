import pytest


class TestRootEndpoint:
    def test_root_redirects_to_static_index(self, client):
        # Arrange
        expected_location = "/static/index.html"

        # Act
        response = client.get("/", follow_redirects=False)

        # Assert
        assert response.status_code == 307
        assert response.headers["location"] == expected_location


class TestActivitiesEndpoint:
    def test_get_activities_returns_activity_data(self, client):
        # Arrange
        expected_activity = "Chess Club"

        # Act
        response = client.get("/activities")

        # Assert
        assert response.status_code == 200
        assert expected_activity in response.json()
        assert "participants" in response.json()[expected_activity]


class TestSignupEndpoint:
    def test_signup_adds_participant(self, client):
        # Arrange
        activity_name = "Art Club"
        email = "student@example.com"

        # Act
        response = client.post(
            f"/activities/{activity_name}/signup", params={"email": email}
        )

        # Assert
        assert response.status_code == 200
        assert email in response.json()["message"]
        assert email in client.get("/activities").json()[activity_name]["participants"]

    def test_duplicate_signup_returns_bad_request(self, client):
        # Arrange
        activity_name = "Art Club"
        email = "student@example.com"
        client.post(f"/activities/{activity_name}/signup", params={"email": email})

        # Act
        response = client.post(
            f"/activities/{activity_name}/signup", params={"email": email}
        )

        # Assert
        assert response.status_code == 400
        assert response.json()["detail"] == "Student is already signed up for this activity"
        participants = client.get("/activities").json()[activity_name]["participants"]
        assert participants.count(email) == 1

    def test_signup_for_unknown_activity_returns_not_found(self, client):
        # Arrange
        activity_name = "Unknown Club"
        email = "student@example.com"

        # Act
        response = client.post(
            f"/activities/{activity_name}/signup", params={"email": email}
        )

        # Assert
        assert response.status_code == 404
        assert response.json()["detail"] == "Activity not found"


class TestRemoveParticipantEndpoint:
    def test_delete_removes_participant(self, client):
        # Arrange
        activity_name = "Art Club"
        email = "student@example.com"
        client.post(f"/activities/{activity_name}/signup", params={"email": email})

        # Act
        response = client.delete(
            f"/activities/{activity_name}/signup", params={"email": email}
        )

        # Assert
        assert response.status_code == 200
        assert email in response.json()["message"]
        assert email not in client.get("/activities").json()[activity_name]["participants"]

    def test_delete_for_unregistered_participant_returns_not_found(self, client):
        # Arrange
        activity_name = "Art Club"
        email = "student@example.com"

        # Act
        response = client.delete(
            f"/activities/{activity_name}/signup", params={"email": email}
        )

        # Assert
        assert response.status_code == 404
        assert response.json()["detail"] == "Student is not signed up for this activity"

    def test_delete_from_unknown_activity_returns_not_found(self, client):
        # Arrange
        activity_name = "Unknown Club"
        email = "student@example.com"

        # Act
        response = client.delete(
            f"/activities/{activity_name}/signup", params={"email": email}
        )

        # Assert
        assert response.status_code == 404
        assert response.json()["detail"] == "Activity not found"


@pytest.mark.parametrize("method, path", [("post", "/activities/Art Club/signup"), ("delete", "/activities/Art Club/signup")])
def test_signup_and_delete_require_email(client, method, path):
    # Arrange
    request = getattr(client, method)

    # Act
    response = request(path)

    # Assert
    assert response.status_code == 422
    assert response.json()["detail"][0]["loc"][-1] == "email"

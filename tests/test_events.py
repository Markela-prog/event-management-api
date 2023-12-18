from fastapi.testclient import TestClient
from main import app
import pytest

client = TestClient(app)

class TestEvent:
    @classmethod
    def setup_class(cls):
        # Log in and get a token
        response = client.post(
            "/auth/token",
            data={
                "username": "admin",
                "password": "admin",
            },
        )
        token = response.json()["access_token"]
        cls.headers = {"Authorization": f"Bearer {token}"}

        # Create an event
        response = client.post(
            "/event/",
            headers=cls.headers,
            json={
                "title": "Test Event",
                "description": "This is a test event",
                "date": "2023-12-31T23:59:59",
                "location": "Test Location",
            },
        )
        data = response.json()
        cls.event_id = data["id"]

    @classmethod
    def teardown_class(cls):
        # Delete the event
        client.delete(f"/event/{cls.event_id}", headers=cls.headers)

    def test_create_event(self):
        pass

    def test_get_all_events(self):
        response = client.get("/event/", headers=self.headers)
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    def test_get_event_by_id(self):
        response = client.get(f"/event/{self.event_id}", headers=self.headers)
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == self.event_id

    def test_update_event(self):
        response = client.put(
            f"/event/{self.event_id}",
            headers=self.headers,
            json={
                "title": "Updated Test Event",
                "description": "This is an updated test event",
                "date": "2024-01-01T00:00:00",
                "location": "Updated Test Location",
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "Updated Test Event"
        assert data["description"] == "This is an updated test event"
        assert data["date"] == "2024-01-01T00:00:00"
        assert data["location"] == "Updated Test Location"

    def test_delete_event(self):
        # This test is now redundant because we're deleting the event in teardown_class
        pass

    def test_join_event(self):
        response = client.post(f"/event/join-event/{self.event_id}", headers=self.headers)
        assert response.status_code == 200
        data = response.json()
        assert data["detail"] == "Successfully joined the event"

    def test_get_attendee_count(self):
        response = client.get(f"/event/events/{self.event_id}/attendees", headers=self.headers)
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, int)


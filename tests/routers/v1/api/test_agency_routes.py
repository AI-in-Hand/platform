from unittest.mock import AsyncMock, patch

from fastapi.testclient import TestClient

from nalgonda.main import app
from nalgonda.models.agency_config import AgencyConfig


def mocked_load(self):  # noqa: ARG001
    return AgencyConfig(
        agency_id="test_agency", agency_manifesto="Test Manifesto", agents=[], agency_chart=[]
    ).model_dump()


def mocked_save(self, data: dict):  # noqa: ARG001
    assert data == {
        "agency_manifesto": "Updated Manifesto",
        "agency_chart": [],
        "agency_id": "test_agency",
        "agents": [],
    }


class MockedAgencyConfigFirestoreStorage:
    def __init__(self, agency_id):
        self.agency_id = agency_id

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

    def load(self):
        return mocked_load(self)

    def save(self, data):
        mocked_save(self, data)


class TestAgencyRoutes:
    client = TestClient(app)

    @patch("nalgonda.models.agency_config.AgencyConfigFirestoreStorage", new=MockedAgencyConfigFirestoreStorage)
    def test_get_agency_config(self):
        response = self.client.get("/v1/api/agency/config?agency_id=test_agency")
        assert response.status_code == 200
        assert response.json() == {
            "agency_id": "test_agency",
            "agency_manifesto": "Test Manifesto",
            "agents": [],
            "agency_chart": [],
        }

    @patch("nalgonda.models.agency_config.AgencyConfigFirestoreStorage", new=MockedAgencyConfigFirestoreStorage)
    @patch("nalgonda.caching.redis_cache_manager.RedisCacheManager.get", new_callable=AsyncMock)
    @patch("nalgonda.caching.redis_cache_manager.RedisCacheManager.set", new_callable=AsyncMock)
    def test_update_agency_config_success(self, mock_redis_set, mock_redis_get):
        new_data = {"agency_manifesto": "Updated Manifesto"}
        response = self.client.put("/v1/api/agency/config?agency_id=test_agency", json=new_data)
        assert response.status_code == 200
        assert response.json() == {"message": "Agency configuration updated successfully"}
        mock_redis_get.assert_called_once()
        mock_redis_set.assert_called_once()

    @patch("nalgonda.models.agency_config.AgencyConfigFirestoreStorage", new=MockedAgencyConfigFirestoreStorage)
    @patch.object(MockedAgencyConfigFirestoreStorage, "load", lambda _: None)
    def test_get_agency_config_not_found(self):
        response = self.client.get("/v1/api/agency/config?agency_id=non_existent_agency")
        assert response.json() == {"detail": "Agency configuration not found"}
        assert response.status_code == 404

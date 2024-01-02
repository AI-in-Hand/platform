from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient

from nalgonda.main import app
from nalgonda.models.agency_config import AgencyConfig
from nalgonda.persistence.agency_config_firestore_storage import AgencyConfigFirestoreStorage


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


class TestAgencyRoutes:
    client = TestClient(app)

    @pytest.mark.skip("Fix the mocks")
    @patch.object(AgencyConfigFirestoreStorage, "load", mocked_load)
    @patch.object(AgencyConfigFirestoreStorage, "save", mocked_save)
    def test_get_agency_config(self):
        response = self.client.get("/v1/api/agency/config?agency_id=test_agency")
        assert response.status_code == 200
        assert response.json() == {
            "agency_id": "test_agency",
            "agency_manifesto": "Test Manifesto",
            "agents": [],
            "agency_chart": [],
        }

    @pytest.mark.skip("Fix the mocks")
    @patch.object(AgencyConfigFirestoreStorage, "load", mocked_load)
    @patch.object(AgencyConfigFirestoreStorage, "save", mocked_save)
    def test_update_agency_config(self):
        new_data = {"agency_manifesto": "Updated Manifesto"}
        response = self.client.put("/v1/api/agency/config?agency_id=test_agency", json=new_data)
        assert response.status_code == 201
        assert response.json() == {"message": "Agency configuration updated successfully"}

    @pytest.mark.skip("Fix the mocks")
    @patch.object(AgencyConfigFirestoreStorage, "load", lambda _: None)
    def test_agency_config_not_found(self):
        response = self.client.get("/v1/api/agency/config?agency_id=non_existent_agency")
        assert response.status_code == 404
        assert response.json() == {"detail": "Agency configuration not found"}

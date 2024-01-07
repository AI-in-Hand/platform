import asyncio
from unittest.mock import AsyncMock, patch

from nalgonda.dependencies.agency_manager import AgencyManager
from nalgonda.models.agency_config import AgencyConfig


class TestAgencyManager:
    @patch("nalgonda.dependencies.agency_manager.RedisCacheManager")
    @patch("nalgonda.dependencies.agency_manager.AgencyConfigFirestoreStorage")
    def test_create_agency(self, mock_firestore_storage, mock_redis_cache):
        # Mock RedisCacheManager
        agency_data = {
            "agency_id": "test_agency",
            "owner_id": "owner_id",
            "agency_manifesto": "Test Agency Manifesto",
            "agents": ["agent1", "agent2"],
            "agency_chart": ["agent1", ["agent2"]],
        }
        agency_config = AgencyConfig(**agency_data)
        mock_redis_cache.get.return_value = None
        mock_redis_cache.set.return_value = AsyncMock()
        mock_firestore_storage.load_or_create.return_value = agency_config

        agency_manager = AgencyManager(redis=mock_redis_cache)
        agency, agency_id = asyncio.run(agency_manager.create_agency())

        assert agency is not None
        assert agency_id == "test_agency"
        assert isinstance(agency_id, str)
        mock_firestore_storage.load_or_create.assert_called_once()
        mock_redis_cache.set.assert_called_with(agency_id, agency)

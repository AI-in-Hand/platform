import json
import logging
from unittest.mock import Mock, patch

from backend.utils.logging_utils.gcloud_logging_handler import create_gcloud_logging_handler


def test_create_gcloud_logging_handler(mocker):
    # Setup
    settings = Mock()
    settings.google_credentials = json.dumps(
        {
            "private_key_id": "private_key_id",
            "private_key": "private_key",
            "client_email": "client_email",
            "client_id": "client_id",
            "type": "service_account",
        }
    )
    settings.google_cloud_log_name = "test-log"

    json_formatter = Mock()
    json_formatter.format.return_value = json.dumps({"message": "test message"})

    # Mocks
    with (
        patch("backend.utils.logging_utils.gcloud_logging_handler.json.loads") as mock_json_loads,
        patch(
            "backend.utils.logging_utils.gcloud_logging_handler.Credentials.from_service_account_info"
        ) as mock_from_service_account_info,
        patch("backend.utils.logging_utils.gcloud_logging_handler.gcloud_logging.Client") as mock_client,
    ):
        # Act
        handler = create_gcloud_logging_handler(settings, json_formatter)

        # Assertions
        assert mock_json_loads.call_count == 1
        assert mock_json_loads.call_args == mocker.call(settings.google_credentials)

        assert mock_from_service_account_info.call_count == 1
        assert mock_from_service_account_info.call_args == mocker.call(mock_json_loads.return_value)

        assert mock_client.call_count == 1
        assert mock_client.call_args == mocker.call(credentials=mock_from_service_account_info.return_value)

        assert mock_client.return_value.logger.call_count == 1
        assert mock_client.return_value.logger.call_args == mocker.call(settings.google_cloud_log_name)

        # Check if the handler is correctly instantiated and set up
        assert isinstance(handler, logging.Handler)
        assert handler.level == logging.INFO

        record = Mock()
        record.levelname = "INFO"
        handler.emit(record)

        assert mock_json_loads.call_count == 2
        assert mock_json_loads.call_args == mocker.call(json_formatter.format.return_value)

        assert mock_client.return_value.logger.return_value.log_struct.call_count == 1
        assert mock_client.return_value.logger.return_value.log_struct.call_args == mocker.call(
            mock_json_loads.return_value, severity="INFO", labels={"service_name": settings.google_cloud_log_name}
        )

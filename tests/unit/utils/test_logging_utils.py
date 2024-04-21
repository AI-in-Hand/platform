import atexit
import logging
import queue
from unittest.mock import MagicMock, call

import pytest

from backend.utils.logging_utils import JSONFormatter, create_gcloud_logging_handler, setup_logging


@pytest.fixture
def mock_logging(mocker):
    # Mock the logging components used in setup_logging
    mocker.patch("logging.handlers.QueueHandler")
    mocker.patch("logging.handlers.QueueListener")
    mocker.patch("logging.handlers.RotatingFileHandler")
    mocker.patch("logging.StreamHandler")
    mocker.patch("logging.Formatter")
    mocker.patch("backend.utils.logging_utils.json_formatter.JSONFormatter")
    mocker.patch("logging.getLogger")
    mocker.patch("atexit.register")
    mocker.patch("queue.Queue")
    # Mock Google Cloud Logging components
    mocker.patch("backend.utils.logging_utils.gcloud_logging_handler.create_gcloud_logging_handler")

    # Return all mocked components for assertions
    return {
        "QueueHandler": logging.handlers.QueueHandler,
        "QueueListener": logging.handlers.QueueListener,
        "RotatingFileHandler": logging.handlers.RotatingFileHandler,
        "StreamHandler": logging.StreamHandler,
        "Formatter": logging.Formatter,
        "JSONFormatter": JSONFormatter,
        "getLogger": logging.getLogger,
        "register": atexit.register,
        "Queue": queue.Queue,
        "create_gcloud_logging_handler": create_gcloud_logging_handler,
    }


def test_setup_logging_handlers_and_levels(mock_logging):
    setup_logging()

    # Assert handlers were created with the correct levels
    mock_logging["RotatingFileHandler"].assert_called_once_with("app.log.jsonl", maxBytes=10485760, backupCount=5)
    file_handler = mock_logging["RotatingFileHandler"].return_value
    file_handler.setLevel.assert_called_once_with(logging.INFO)

    mock_logging["StreamHandler"].assert_called_once()
    stderr_handler = mock_logging["StreamHandler"].return_value
    stderr_handler.setLevel.assert_called_once_with(logging.INFO)

    # Assert formatters were set correctly
    file_handler.setFormatter.assert_called_once()
    stderr_handler.setFormatter.assert_called_once()


def test_setup_logging_queue_and_listener_started(mock_logging):
    setup_logging()

    # Assert the QueueHandler and QueueListener were started
    mock_logging["QueueListener"].assert_called_once()
    listener = mock_logging["QueueListener"].return_value
    listener.start.assert_called_once()
    mock_logging["register"].assert_called_once_with(listener.stop)


def test_setup_logging_root_logger_config(mock_logging):
    setup_logging()
    root_logger = mock_logging["getLogger"].return_value

    # Check that the root logger's level was set to DEBUG initially
    assert root_logger.setLevel.call_args_list[0] == call(logging.DEBUG)

    # Check subsequent calls to setLevel for specific loggers
    specific_logger_calls = [
        call(logging.ERROR),  # For passlib.handlers.bcrypt
        call(logging.ERROR),  # For googleapiclient.discovery_cache
        call(logging.WARNING),  # For openai
    ]

    # Validate the specific logger level settings
    assert root_logger.setLevel.call_args_list[1:] == specific_logger_calls


def test_silence_specific_logger(mock_logging):
    setup_logging()

    # Assert specific loggers are silenced as expected
    bcrypt_logger = mock_logging["getLogger"].call_args_list[-3][0][0]
    assert bcrypt_logger == "passlib.handlers.bcrypt"
    mock_logging["getLogger"].return_value.setLevel.assert_called_with(logging.WARNING)


def test_google_cloud_logging_handler_setup(mock_logging):
    mock_logging["create_gcloud_logging_handler"].return_value = MagicMock()
    setup_logging()
    # Assert the Google Cloud Logging handler was setup correctly
    mock_logging["create_gcloud_logging_handler"].assert_called_once()

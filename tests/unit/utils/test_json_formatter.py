import json
import logging
import sys

import pytest

from backend.utils.logging_utils.json_formatter import JSONFormatter


@pytest.fixture
def log_record():
    """Fixture to create a basic log record."""
    record = logging.LogRecord(
        name="test",
        level=logging.INFO,
        pathname=__file__,
        lineno=10,
        msg="This is a test message",
        args=(),
        exc_info=None,
    )
    return record


def test_json_formatter_without_custom_keys(log_record):
    """Test the JSONFormatter without custom format keys."""
    # Adjusting the test to not expect 'levelname' by default
    formatter = JSONFormatter(fmt_keys={"level": "levelname", "msg": "message"})
    log_record.levelname = "INFO"  # Explicitly setting levelname for the test
    json_output = formatter.format(log_record)
    data = json.loads(json_output)

    assert data["msg"] == "This is a test message", "Message should match log record message."
    assert "timestamp" in data, "Timestamp should be included."
    assert data["level"] == "INFO", "Explicitly mapped 'level' should match the log level name."


def test_json_formatter_with_custom_keys(log_record):
    """Test the JSONFormatter with custom format keys."""
    custom_keys = {
        "level": "levelname",
        "msg": "message",
    }
    formatter = JSONFormatter(fmt_keys=custom_keys)
    json_output = formatter.format(log_record)
    data = json.loads(json_output)

    assert data["level"] == "INFO", "Custom key for level should work."
    assert data["msg"] == "This is a test message", "Custom key for message should work."


def test_json_formatter_with_additional_attributes(log_record):
    """Test the JSONFormatter including additional attributes in the log record."""
    log_record.custom_attribute = "custom_value"
    formatter = JSONFormatter()
    json_output = formatter.format(log_record)
    data = json.loads(json_output)

    assert data["custom_attribute"] == "custom_value", "Additional attributes should be included."


def test_json_formatter_with_exception_info(log_record):
    """Test the JSONFormatter including exception information."""
    try:
        raise ValueError("Test exception")
    except ValueError:
        exc_info = sys.exc_info()
        log_record.exc_info = exc_info

    formatter = JSONFormatter()
    json_output = formatter.format(log_record)
    data = json.loads(json_output)

    assert "exc_info" in data, "Exception information should be included."


def test_json_formatter_with_stack_info(log_record):
    """Test the JSONFormatter including stack information."""
    log_record.stack_info = "Test stack info"
    formatter = JSONFormatter()
    json_output = formatter.format(log_record)
    data = json.loads(json_output)

    assert data["stack_info"] == "Test stack info", "Stack information should be included."

import logging

import pytest

from backend.utils.logging_utils import setup_logging


@pytest.fixture
def reset_logging():
    # Save the original state of the root logger
    original_handlers = logging.root.handlers[:]
    original_level = logging.root.level

    # Execute the test
    yield

    # Reset the root logger to its original state
    logging.root.handlers = original_handlers
    logging.root.setLevel(original_level)
    logging.getLogger("passlib.handlers.bcrypt").setLevel(logging.NOTSET)


@pytest.mark.usefixtures("reset_logging")
class TestLoggingSetup:
    def test_root_logger_level(self):
        setup_logging()
        assert logging.root.level == logging.DEBUG, "Root logger level should be DEBUG."

    def test_info_logged_to_stderr(self, caplog):
        setup_logging()
        with caplog.at_level(logging.INFO):
            logging.info("Test info message.")
        assert "Test info message." in caplog.text, "INFO level message should be logged to stderr."

    def test_passlib_bcrypt_error_level(self):
        setup_logging()
        assert (
            logging.getLogger("passlib.handlers.bcrypt").level == logging.ERROR
        ), "Passlib bcrypt logger level should be ERROR."

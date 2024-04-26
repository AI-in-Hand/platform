import atexit
import logging
import logging.config
import logging.handlers
import queue

from backend.settings import settings
from backend.utils.logging_utils.gcloud_logging_handler import create_gcloud_logging_handler
from backend.utils.logging_utils.json_formatter import JSONFormatter


def setup_logging():
    """
    Set up the logging configuration for the application. This function will configure the root logger to use a
    QueueHandler and QueueListener to handle log records. The QueueListener will handle the log records and send them to
    the appropriate handlers. The handlers will be configured to log to the console and to a file. If the application is
    running in a production environment, the handler will also log to Google Cloud Logging.
    """
    # Configure formatters
    simple_formatter = logging.Formatter(
        "[%(levelname)s|%(module)s|L%(lineno)d] %(asctime)s: %(message)s", "%Y-%m-%dT%H:%M:%S%z"
    )
    json_formatter = JSONFormatter(
        fmt_keys={
            "level": "levelname",
            "message": "message",
            "timestamp": "timestamp",
            "logger": "name",
            "module": "module",
            "function": "funcName",
            "line": "lineno",
            "thread_name": "threadName",
        }
    )

    # Initialize the log queue
    log_queue = queue.Queue()

    # Create and configure handlers
    stdout_handler = logging.StreamHandler()
    stdout_handler.setFormatter(simple_formatter)
    stdout_handler.setLevel(logging.INFO)

    # file_handler = logging.handlers.RotatingFileHandler("app.log.jsonl", maxBytes=10485760, backupCount=5)
    # file_handler.setFormatter(json_formatter)
    # file_handler.setLevel(logging.INFO)

    gcloud_handler = create_gcloud_logging_handler(settings, json_formatter)

    # Create QueueHandler and QueueListener
    handlers = [stdout_handler]  # file_handler]
    if gcloud_handler:
        handlers.append(gcloud_handler)
    queue_handler = logging.handlers.QueueHandler(log_queue)
    listener = logging.handlers.QueueListener(log_queue, *handlers, respect_handler_level=True)

    # Start the listener
    listener.start()
    atexit.register(listener.stop)

    # Configure the root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)
    root_logger.addHandler(queue_handler)

    # Silence passlib and other library warning messages
    logging.getLogger("passlib.handlers.bcrypt").setLevel(logging.ERROR)
    logging.getLogger("googleapiclient.discovery_cache").setLevel(logging.ERROR)
    logging.getLogger("openai").setLevel(logging.WARNING)

    root_logger.info("Logging setup complete")

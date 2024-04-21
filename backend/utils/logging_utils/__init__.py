import atexit
import json
import logging
import logging.config
import logging.handlers
import queue

from google.cloud import logging as gcloud_logging

from backend.settings import settings
from backend.utils.logging_utils.json_formatter import JSONFormatter


def setup_logging():
    """
    Setup the logging configuration for the application to include Google Cloud Logging.
    """
    log_name = settings.google_cloud_log_name
    project_id = settings.google_cloud_project

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
    stderr_handler = logging.StreamHandler()
    stderr_handler.setFormatter(simple_formatter)
    stderr_handler.setLevel(logging.WARNING)

    file_handler = logging.handlers.RotatingFileHandler("app.log.jsonl", maxBytes=10485760, backupCount=5)
    file_handler.setFormatter(json_formatter)
    file_handler.setLevel(logging.DEBUG)

    # Google Cloud Logging Handler
    if project_id:
        client = gcloud_logging.Client()
        cloud_logger = client.logger(log_name)

        class GCloudLoggingHandler(logging.Handler):
            def emit(self, record):
                log_entry = json.loads(json_formatter.format(record))
                cloud_logger.log_struct(log_entry, severity=record.levelname, labels={"backend": log_name})

        gcloud_handler = GCloudLoggingHandler()
        gcloud_handler.setLevel(logging.INFO)
    else:
        gcloud_handler = None

    # Create QueueHandler and QueueListener
    handlers = [stderr_handler, file_handler]
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

    root_logger.info("Logging setup complete with Google Cloud integration.")

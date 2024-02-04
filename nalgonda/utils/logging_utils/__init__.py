import atexit
import logging
import logging.config
import logging.handlers
import queue

from nalgonda.utils.logging_utils.json_formatter import JSONFormatter


def setup_logging():
    """
    Setup the logging configuration for the application. This function will configure the root logger to use a
    QueueHandler and QueueListener to handle log records. The QueueListener will handle the log records and send them to
    a StreamHandler and a RotatingFileHandler. The StreamHandler will log WARNING and above to stderr, and the
    RotatingFileHandler will log DEBUG and above to a file. The log records will be formatted using a simple formatter
    for the StreamHandler and a JSONFormatter for the RotatingFileHandler.
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
    stderr_handler = logging.StreamHandler()
    stderr_handler.setFormatter(simple_formatter)
    stderr_handler.setLevel(logging.INFO)

    file_handler = logging.handlers.RotatingFileHandler("app.log.jsonl", maxBytes=10485760, backupCount=5)
    file_handler.setFormatter(json_formatter)
    file_handler.setLevel(logging.INFO)

    # Create QueueHandler and QueueListener
    queue_handler = logging.handlers.QueueHandler(log_queue)
    listener = logging.handlers.QueueListener(log_queue, stderr_handler, file_handler, respect_handler_level=True)

    # Start the listener
    listener.start()
    atexit.register(listener.stop)

    # Configure the root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)
    root_logger.addHandler(queue_handler)

    # Silence passlib warning messages
    logging.getLogger("passlib.handlers.bcrypt").setLevel(logging.ERROR)

    root_logger.info("Logging setup complete.")

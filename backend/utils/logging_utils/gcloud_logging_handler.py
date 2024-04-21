import json
import logging

from google.cloud import logging as gcloud_logging
from google.oauth2.service_account import Credentials


def create_gcloud_logging_handler(settings, json_formatter):
    if settings.google_credentials:
        credentials_dict = json.loads(settings.google_credentials)
        credentials = Credentials.from_service_account_info(credentials_dict)
        client = gcloud_logging.Client(credentials=credentials)
        cloud_logger = client.logger(settings.google_cloud_log_name)

        class GCloudLoggingHandler(logging.Handler):
            def emit(self, record):
                log_entry = json.loads(json_formatter.format(record))
                cloud_logger.log_struct(
                    log_entry, severity=record.levelname, labels={"service_name": settings.google_cloud_log_name}
                )

        gcloud_handler = GCloudLoggingHandler()
        gcloud_handler.setLevel(logging.INFO)
        return gcloud_handler
    return None

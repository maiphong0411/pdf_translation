import json
import logging
import os
import sys

DEFAULT_FORMAT = logging.Formatter(
    "[%(asctime)s] [%(levelname)s] [%(filename)s:%(lineno)d] %(message)s"
)

DEFAULT_LOG_DIR = os.path.dirname(os.path.realpath(__file__)) + "/../../logs"
os.makedirs(DEFAULT_LOG_DIR, exist_ok=True)

DEFAULT_LOG_FILE = "rag4sac.log"


def namer(name):
    return name


def get_file_handler(formatter, log_filename):
    file_handler = logging.FileHandler(log_filename)
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)
    return file_handler


def get_stream_handler(formatter):
    stream_handler = logging.StreamHandler(sys.stdout)
    stream_handler.setLevel(logging.DEBUG)
    stream_handler.setFormatter(formatter)
    return stream_handler


def get_logger(name, formatter=DEFAULT_FORMAT, log_filename=DEFAULT_LOG_FILE):
    log_filename = os.path.join(DEFAULT_LOG_DIR, log_filename)
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)
    logger.addHandler(get_stream_handler(formatter))
    if log_filename:
        logger.addHandler(get_file_handler(formatter, log_filename))
    return logger


def get_app_log(record):
    import datetime

    timestamp = datetime.datetime.fromtimestamp(record.created).strftime(
        "%Y-%m-%dT%H:%M:%S.%f"
    )[:-2]
    json_obj = {
        "time": timestamp,
        "service_name": "chatbot",
        "level": record.levelname,
        "message": record.message,
    }

    return json_obj


def get_access_log(record):
    import datetime

    timestamp = datetime.datetime.fromtimestamp(record.created).strftime(
        "%Y-%m-%dT%H:%M:%S.%f"
    )[:-2]
    json_obj = {
        "time": timestamp,
        "service_name": "chatbot",
        "level": record.levelname,
        "message": record.message,
        "req": record.extra_info["req"],
        "res": record.extra_info["res"],
    }

    return json_obj


class CustomFormatter(logging.Formatter):
    def __init__(self, formatter):
        logging.Formatter.__init__(self, formatter)

    def format(self, record):
        logging.Formatter.format(self, record)
        if not hasattr(record, "extra_info"):
            return json.dumps(get_app_log(record))
        else:
            return json.dumps(get_access_log(record))

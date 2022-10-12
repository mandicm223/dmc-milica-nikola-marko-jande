import logging
import os
import sys
from pythonjsonlogger import jsonlogger


class LogFilter(logging.Filter):
    """
    Used by :func:`initialize_logger` to redirect errors to ``stderr``
    """

    def filter(self, rec):
        return rec.levelno in (logging.DEBUG, logging.INFO, logging.WARNING)


class JsonFormatterWrapper(jsonlogger.JsonFormatter):
    def add_fields(self, log_record, record, message):
        super(JsonFormatterWrapper, self).add_fields(log_record, record, message)
        if 'AWS_LAMBDA_FUNCTION_NAME' in os.environ:
            log_record['awsService'] = "aws:lambda"
            log_record['awsFunctionName'] = os.environ['AWS_LAMBDA_FUNCTION_NAME']


def initialize_logger() -> logging.Logger:
    """
    Log initialization

    :return: logger object
    """

    levels = {'DEBUG': logging.DEBUG,
              'INFO': logging.INFO,
              'WARNING': logging.WARNING,
              'ERROR': logging.ERROR}

    log_level = levels[os.getenv('LOGGER_LVL', 'INFO').upper()]
    logger = logging.getLogger()

    formatter = JsonFormatterWrapper(
        "%(levelname)s\n%(asctime)s\n%(filename)s\n%(funcName)s\n%(lineno)d\n%(message)s\n")

    stdout_handler = logging.StreamHandler(sys.stdout)
    stdout_handler.setLevel(logging.DEBUG)
    stdout_handler.addFilter(LogFilter())
    stdout_handler.setFormatter(formatter)
    stderr_handler = logging.StreamHandler(sys.stderr)
    stderr_handler.setLevel(logging.ERROR)
    stderr_handler.setFormatter(formatter)
    logger.propagate = 0
    logger.addHandler(stdout_handler)
    logger.addHandler(stderr_handler)
    logger.setLevel(log_level)
    return logger


log: logging.Logger = initialize_logger()

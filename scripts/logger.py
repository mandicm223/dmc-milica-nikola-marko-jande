import logging
import os
import sys


class LogFilter(logging.Filter):
    """
    Used by :func:`initialize_logger` to redirect errors to ``stderr``
    """

    def filter(self, rec):
        return rec.levelno in (logging.DEBUG, logging.INFO, logging.WARNING)


class CustomFormatter(logging.Formatter):
    green = '\x1b[38;5;76m'
    grey = '\x1b[38;21m'
    yellow = '\x1b[38;5;226m'
    red = '\x1b[38;5;196m'
    bold_red = '\x1b[31;1m'
    reset = '\x1b[0m'

    def __init__(self, fmt):
        super().__init__()
        self.fmt = fmt
        self.FORMATS = {
            logging.DEBUG: self.grey + self.fmt + self.reset,
            logging.INFO: self.green + self.fmt + self.reset,
            logging.WARNING: self.yellow + self.fmt + self.reset,
            logging.ERROR: self.red + self.fmt + self.reset,
            logging.CRITICAL: self.bold_red + self.fmt + self.reset
        }

    def format(self, record):
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt, datefmt="%Y-%m-%d %H:%M:%S")
        return formatter.format(record)


def initialize_logger() -> logging.Logger:
    """
    Log initialization

    :param module_name: module name
    :return: logger object
    """

    levels = {'DEBUG': logging.DEBUG,
              'INFO': logging.INFO,
              'WARNING': logging.WARNING,
              'ERROR': logging.ERROR}
    log_level = levels[os.getenv('LOGGER_LVL', 'INFO').upper()]
    logger = logging.getLogger()

    log_fmt_string = '%(asctime)-19s %(funcName)s: [%(levelname)s] - %(message)s'
    formatter = CustomFormatter(fmt=log_fmt_string)

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

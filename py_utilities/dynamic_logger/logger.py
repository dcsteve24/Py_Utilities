""" Wrapper around the Python logging utility for functions to create and use a logging object
without a need to pass it around or import a bunch of crud per module.

Adds some usability and functionality such as passing str levels, standardizes, the local log
outputs/formats, and enables easy to use logging.

Usage:
    In most cases you will not want the defaults, however, you could run log_message right out of
    the box and it would create a logger with all the defaults specified under create_logger.

    But since you usually need more specific configurations, its better to import create_logger
    and run it as one of the first actions at your entry point with your required args. Afterwards,
    you DO NOT need to pass around that object unless desired. Instead import and use log_message to
    automatically pull and find the object before logging the message.

__constants__:
    ACCEPTED_LOG_LEVELS
    _DEFAULT_LOGGING_PATH
    _FORMATTER

__functions__:
    _level_value_check
    create_logger
    log_message

@author: dcsteve24
__python_version__ = Py2/Py3
__os__ = Windows/Linux
__updated__ = '2021-09-04'
"""

import logging.handlers
import os
import sys

# Default logging path to the home directory -- for troubleshooting/debugging
_DEFAULT_LOGGING_PATH = os.path.join(os.path.expanduser('~'), 'python_debug.log')
# Logging Format
_FORMATTER = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
# The acceptable log level values
ACCEPTED_LOG_LEVELS = {'debug': logging.DEBUG,  # 10
                       'info': logging.INFO,  # 20
                       'warn': logging.WARN,  # 30
                       'warning': logging.WARNING,  # 30
                       'error': logging.ERROR,  # 40
                       'critical': logging.CRITICAL,  # 50
                       'fatal': logging.FATAL}  # 50


def _level_value_check(level):
    """ Helper to check values of the passed log level to ensure a proper value is set. Also
    converts to an int if a str type is passed. Errors if the value is not an acceptable value.

    Args:
        level: Str or Int. The log level trying to be utilized. See the above global for acceptable
            values.

    Returns:
        int value of equivalent level passed.

    Raises:
        ValueError: Bad log level value was passed.
    """
    if type(level) is int:
        if level in ACCEPTED_LOG_LEVELS.values():
            return level
    elif type(level) is str:
        level = level.lower()
        if level in ACCEPTED_LOG_LEVELS:
            return ACCEPTED_LOG_LEVELS[level]
    raise ValueError(
        'log level was not an acceptable value of str: %s or int: %s' %
        (', '.join(ACCEPTED_LOG_LEVELS), ', '.join(str(x) for x in ACCEPTED_LOG_LEVELS.values())))


def create_logger(log_path=DEFAULT_LOGGING_PATH,
                  level='info',
                  identifiter=__name__,
                  backup_count=5,
                  rotate_size=10737418240,
                  console_output=False):
    """ Configures and returns a Python logger object. If one already exists for the name, it will
    return that one instead of creating it.

    NOTE: This is based on your Python instance. It is critical to understand when you use this
    across multiple modules, the first one to create the logging identifier instance will be the
    settings you get every time. This module does not allow modification to existing loggers to
    prevent issues with duplicate handlers (outside the ability to add a console output if one was
    not added at creation) . Therefore, it is recommended to create unique identifiers per log
    setting desired (e.g. file location, or log levels) and call those specific identifiers where
    needed. You can have as many of these identifiers as needed each with same, similar, or
    different settings.

    Args:
        Optional:
            log_path: Str. The abs path to store logs into. Defaults to the path specified in the
                global.
            level: Str or Int. The level of the logger. This affects what is written to the log.
                E.g. if code generates a debug message but you configured the logger at an info
                level, the logger will not write the message to the handlers. Accepts the values
                specified in the global above. Defaults to 'info'.
            identifier: Str. The logger unique identifier. Defaults to the name of this module.
            backup_count: Int. If set the logger will keep this amount of log files archived when
                rotating. This has no effect if rotate_size is 0. If this is 0 a backup is never
                kept. Rotated logs are stored with a sequential number appended (e.g. <log_path.1,
                <log_path>.2, etc.) This defaults to 5.
            rotate_size: Int. The size in bytes we rotate the log at. If backup_count is higher than
                0 it will keep the rotated log. Otherwise it will erase and restart the log file. A
                value of 0 will result in a indefinite size (never rotating). Defaults to
                10737418240 (10GB).
            console_output: Bool. If True will add a stdout handler which serves the same purpose
                of print statements. You will get the same log message in both the console and the
                file.

    Returns:
        The configured Python logging object. PASSING THIS AROUND IS OPTIONAL (not recommended).
    """
    # Value check and force to int
    level = _level_value_check(level)
    # Create/Grab logger object
    logger = logging.getLogger(identifiter)
    if not getattr(logger, 'handlers', None):
        logger.setLevel(level)
        logger.propagate = False
        # Configure file handler
        log_handler = logging.handlers.RotatingFileHandler(
            log_path, maxBytes=rotate_size, backupCount=backup_count, mode='a')
        log_handler.setLevel(level)
        log_handler.setFormatter(FORMATTER)
        logger.addHandler(log_handler)
    # Configure console output handler
    if console_output and logging.StreamHandler not in (type(x) for x in logger.handlers):
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(level)
        console_handler.setFormatter(FORMATTER)
        logger.addHandler(console_handler)
    return logger


def log_message(level, message, logger_id=__name__):
    """ Helper to log a message to the passed logger. Prevents need of importing/knowing the logging
    module INFO, DEBUG, etc. in your module and prevents the passing of the object around; though
    you can still do this if desired. Instead, call this with the logger_id defaults or set a global
    with your logger name and call this with that per identifier.

    Recommend creating a logger before running this so you get the functionality you expect!

    Args:
        level: Str or Int. The level of the log message. See the global above for acceptable values.
        message: Str. The message we are logging.

        Optional:
            logger_id: Str or logging.Logger object. The logger unique identifier to use for logging
                or the configured logging.Logger object. If a logger with the logger identifier
                exists in this Python instance it will pull that logger and its configurations and
                log to it. If this object does not exist, it will create it with the default args
                in create_logger.
    """
    level = _level_value_check(level)
    if type(logger_id) is logging.Logger:
        logger = logger_id
    else:
        logger = create_logger(identifier=logger_id)
    logger.log(level, message)

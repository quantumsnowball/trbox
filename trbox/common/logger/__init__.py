from collections.abc import Callable
import logging
from logging import getLogger, Formatter, StreamHandler
from typing import Any


# types
LoggerFunction = Callable[[Any, ], None]


# level names
LEVELS = ['debug', 'info', 'warning', 'error', 'critical']

# raw parts
DATETIME = '%(asctime)s'
DATE_FORMAT = '%Y-%m-%d %H:%M:%S'
MSECOND = '%(msecs)03d'
LEVELNAME_RIGHT = '%(levelname)5s'
MESSAGE = '%(message)s'
PROCESS = '%(process)d'
PROCESS_NAME = '%(processName)s'
THREAD = '%(thread)s'
THREAD_NAME = '%(threadName)s'
NAME = '%(name)s'
MODULE = '%(module)s'
FILENAME = '%(filename)s'
FUNCTION_NAME = '%(funcName)s'
LINENO = '%(lineno)s'

# combo parts
TRACE_INFO = f'{MODULE} > {FILENAME}:{LINENO} > {FUNCTION_NAME}() #{NAME}'
EXTRA_INFO = f'@{PROCESS_NAME}({PROCESS}) @{THREAD_NAME}({THREAD})'

PREFIX = f'[ {DATETIME}.{MSECOND} | {LEVELNAME_RIGHT} ]'
SUFFIX = f'[ {TRACE_INFO} ]'
SUFFIX_LONG = f'[ {TRACE_INFO} {EXTRA_INFO} ]'

# presets
BASIC = f'{PREFIX} {MESSAGE}'
NORMAL = f'{BASIC} {SUFFIX}'
DETAIL = f'{BASIC} {SUFFIX_LONG}'

FORMAT_STRINGS = {lv: NORMAL if lv in ('info', 'warning') else DETAIL
                  for lv in LEVELS}


def make_logging_function() -> tuple[LoggerFunction, ...]:
    '''
    Each level has its own logger with its specific formatter, representing
    different level of message detail.
    '''
    # formatters
    fmts = {lv: Formatter(fmt=fs,
                          datefmt=DATE_FORMAT)
            for lv, fs in FORMAT_STRINGS.items()}

    # loggers
    def make_log_fn(lv: str, fmt: Formatter) -> LoggerFunction:
        # create logger with level name
        logger = getLogger(lv)
        # clear any existing handlers
        if logger.hasHandlers():
            logger.handlers.clear()
        # add handler(s)
        sh = StreamHandler()
        sh.setFormatter(fmt)
        logger.addHandler(sh)
        # extract the matching logging function
        fn: LoggerFunction = getattr(logger, lv)
        return fn

    # only need the log function matching each level logger
    fns = tuple(make_log_fn(lv, fmt)
                for lv, fmt in fmts.items())
    exception = getLogger('error').exception
    return *fns, exception


# import these function directly in other source files
debug, info, warning, error, critical, exception = make_logging_function()


def set_log_level(lv: str) -> None:
    loggers = [logging.getLogger(name)
               for name in logging.root.manager.loggerDict]
    for logger in loggers:
        logger.setLevel(lv.upper())


def eval_format_string() -> None:
    '''
    Pytest seems to override the formatter with its own, therefore when using
    pytest, need to set them manually by copy and pasting the string into
    pytest.ini. Run this python script directly in the shell to get these
    format string.

    For shell stdout, use BASIC or NORMAL is more appropriate. For file log,
    use DETAIL to include much more information for debugging.
    '''
    print(f'BASIC = {BASIC}')
    print(f'NORMAL = {NORMAL}')
    print(f'DETAIL = {DETAIL}')


if __name__ == '__main__':
    eval_format_string()

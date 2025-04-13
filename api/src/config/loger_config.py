import logging.config

LOGGER_CONFIG = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'standard': {
            'format': '%(asctime)s [%(levelname)s] %(name)s: %(message)s',
            'datefmt': '%Y-%d-%m %I:%M:%S',
        },
        'json': {
            'format': '{"asctime": "%(asctime)s", "name": "%(name)s", "lavelname": "%(levelname)s", "message": "%(message)s"}',
            'datefmt': '%Y-%d-%m %I:%M:%S',
        },
        'min': {
            'format': '%(levelname)s [%(name)s:] %(message)s',
        },
        'colored': {
            '()': 'colorlog.ColoredFormatter',
            'format': "%(log_color)s%(levelname)-10s%(reset)s %(blue)s%(name)-10s %(white)s%(message)s"
        },
    },
    'handlers': {
        'default': {
            'class': 'logging.StreamHandler',
            # 'formatter': 'json',
            'formatter': 'colored',
            # 'level': 'INFO',
            # 'stream': 'ext://sys.stdout',  # Default is stderr
        },
    },
    'loggers': {
        '': {  # root logger
            'handlers': ['default'],
            'level': 'INFO',
            # 'propagate': False
        },
        'httpx': {
            'handlers': ['default'],
            'level': 'WARNING',
        }
    }
}


def loger_init():
    logging.config.dictConfig(LOGGER_CONFIG)

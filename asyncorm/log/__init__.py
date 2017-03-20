import logging

from logging.config import dictConfig
from os import path

LOG_DIR = path.join(path.abspath(path.abspath(path.dirname(__file__))))

LOGLEVEL = 'INFO'


logging_config = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'normal': {
            'format': '%(asctime)s %(name)s - %(levelname)s: %(message)s'
        },
    },
    'handlers': {
        'main_logger': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': path.join(
                LOG_DIR,
                'asyncorm.log',
            ),
            'formatter': 'normal'
        },
        'stream': {
            'level': LOGLEVEL,
            'class': 'logging.StreamHandler',
            'formatter': 'normal'
        },
    },
    'loggers': {
        'asyncorm': {
            # 'handlers': ['stream', ],
            'handlers': ['stream', 'main_logger'],
            'propagate': True,
            'level': LOGLEVEL,
        },
    }
}

dictConfig(logging_config)


logger = logging.getLogger('asyncorm')

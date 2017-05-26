import logging

from logging.config import dictConfig

# LOGLEVEL = 'DEBUG'
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
        'stream': {
            'level': LOGLEVEL,
            'class': 'logging.StreamHandler',
            'formatter': 'normal'
        },
    },
    'loggers': {
        'asyncorm': {
            'handlers': ['stream', ],
            'propagate': True,
            'level': LOGLEVEL,
        },
    }
}

dictConfig(logging_config)


logger = logging.getLogger('asyncorm')

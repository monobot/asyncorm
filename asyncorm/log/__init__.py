import logging
from logging.config import dictConfig

LOGLEVEL = "INFO"


logging_config = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "normal": {"format": "%(asctime)s %(name)s - %(levelname)s: %(message)s"},
        "raw_message": {"format": "%(message)s"},
    },
    "handlers": {
        "stream": {"level": LOGLEVEL, "class": "logging.StreamHandler", "formatter": "normal"},
        "raw_stream": {"level": LOGLEVEL, "class": "logging.StreamHandler", "formatter": "raw_message"},
    },
    "loggers": {
        "asyncorm": {"handlers": ["stream"], "propagate": True, "level": LOGLEVEL},
        "asyncorm_stream": {"handlers": ["raw_stream"], "propagate": True, "level": LOGLEVEL},
    },
}

dictConfig(logging_config)


logger = logging.getLogger("asyncorm")

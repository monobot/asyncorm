import logging
import os


logger = logging.getLogger('asyncorm')


class AppConfig:
    name = NotImplementedError()
    dir_name = os.getcwd()

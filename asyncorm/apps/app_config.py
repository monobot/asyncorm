import logging
import os


logger = logging.getLogger('asyncorm')


class AppConfig:
    name = ''
    dir_name = os.getcwd()

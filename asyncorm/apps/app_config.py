import logging

logger = logging.getLogger("asyncorm")


class AppConfig:
    """
    AppConfig is the hook class to be able to inspect the code and
    find where your apps will be defined.
    """

    name = ""

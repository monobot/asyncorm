__all__ = (
    "AsyncOrmAppError",
    "AsyncOrmCommandError",
    "AsyncOrmConfigError",
    "AsyncormException",
    "AsyncOrmFieldError",
    "AsyncOrmMigrationError",
    "AsyncOrmModelDoesNotExist",
    "AsyncOrmModelError",
    "AsyncOrmMultipleObjectsReturned",
    "AsyncOrmQuerysetError",
    "AsyncOrmSerializerError",
)


class AsyncormException(Exception):
    pass


class AsyncOrmCommandError(AsyncormException):
    """Exceptions to be raised when command errors"""

    pass


class AsyncOrmFieldError(AsyncormException):
    """to be raised when there are field errors detected"""

    pass


class AsyncOrmModelError(AsyncormException):
    """to be raised when there are model errors detected"""

    pass


class AsyncOrmQuerysetError(AsyncormException):
    """to be raised when there are queryset errors detected"""

    pass


class AsyncOrmConfigError(AsyncormException):
    """to be raised when there are configuration errors detected"""

    pass


class AsyncOrmMigrationError(AsyncormException):
    """to be raised when there are configuration errors detected"""

    pass


class AsyncOrmModelDoesNotExist(AsyncormException):
    """to be raised when there are model errors detected"""

    pass


class AsyncOrmMultipleObjectsReturned(AsyncormException):
    """to be raised when there are model errors detected"""

    pass


class AsyncOrmSerializerError(AsyncormException):
    """to be raised when there are model errors detected"""

    pass


class AsyncOrmAppError(AsyncormException):
    """to be raised when there are class App or config errors detected"""

    pass

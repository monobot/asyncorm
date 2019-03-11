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
    "AsyncormTransactionRollback",
)


class AsyncormException(Exception):
    pass


class AsyncormTransactionRollback(Exception):
    """Raised when we want to force a transaction rollback."""

    pass


class AsyncOrmCommandError(AsyncormException):
    """Exceptions Raised when command errors"""

    pass


class AsyncOrmFieldError(AsyncormException):
    """Raised when there are field errors detected."""

    pass


class AsyncOrmModelDoesNotExist(AsyncormException):
    """Raised when the object requested does not exist."""

    pass


class AsyncOrmModelNotDefined(AsyncormException):
    """Raised when the model does not exist in the ORM."""

    pass


class AsyncOrmModelError(AsyncormException):
    """Raised when there are model errors detected."""

    pass


class AsyncOrmQuerysetError(AsyncormException):
    """Raised when there are queryset errors detected."""

    pass


class AsyncOrmConfigError(AsyncormException):
    """Raised when there are configuration errors detected."""

    pass


class AsyncOrmMigrationError(AsyncormException):
    """Raised when there are configuration errors detected."""

    pass


class AsyncOrmMultipleObjectsReturned(AsyncormException):
    """Raised when there are model errors detected."""

    pass


class AsyncOrmSerializerError(AsyncormException):
    """Raised when there are model errors detected."""

    pass


class AsyncOrmAppError(AsyncormException):
    """Raised when there are class App or configuration errors detected."""

    pass

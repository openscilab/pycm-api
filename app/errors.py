"""PyCM API errors."""


class PyCMAPIBaseError(Exception):
    """Base error class."""

    pass


class PyCMAPISaveFileError(PyCMAPIBaseError):
    """Save file error class."""

    pass

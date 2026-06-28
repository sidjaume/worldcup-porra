class DomainError(Exception):
    """Base exception for domain rule violations."""


class PredictionLockedError(DomainError):
    """Raised when a prediction is submitted after the lock time."""


class InvalidMatchResultError(DomainError):
    """Raised when a match result cannot produce a valid knockout winner."""


class BracketProgressionError(DomainError):
    """Raised when a winner cannot advance through the configured bracket."""


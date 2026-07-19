from .business_exception import BusinessException


class ExperimentStateConflictException(BusinessException):
    """Raised when an experiment state transition is invalid."""

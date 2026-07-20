from .business_exception import BusinessException


class ExperimentRunStateConflictException(BusinessException):
    """Raised when an experiment run state transition is invalid."""

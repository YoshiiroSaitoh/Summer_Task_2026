from .business_exception import BusinessException


class ExperimentRunNotFoundException(BusinessException):
    """Raised when an experiment run cannot be found."""

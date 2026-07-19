from .business_exception import BusinessException


class ExperimentNotFoundException(BusinessException):
    """Raised when an experiment cannot be found."""

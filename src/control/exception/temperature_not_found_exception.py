from .business_exception import BusinessException


class TemperatureNotFoundException(BusinessException):
    """Raised when a temperature record cannot be found."""

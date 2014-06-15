# -*- coding: utf-8 -*-

class SuspiciousOperation(Exception):
    "The user did something suspicious"
    pass

class ImproperlyConfigured(Exception):
    "Django is somehow improperly configured"
    pass

class InitFailed(Exception):
    "The user did something suspicious"
    pass


class BaeApiException(Exception):
    """
    The base class of Bae api exception
    """
    pass

class BaeParamError(BaeApiException):
    pass

class BaeValueError(BaeApiException):
    pass

class BaeBackendError(BaeApiException):
    pass

class BaeConstructError(BaeApiException):
    pass

class BaeOperationFailed(BaeApiException):
    pass


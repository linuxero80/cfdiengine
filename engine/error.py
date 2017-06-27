import enum


class ErrorCode(enum.Enum):
    """
    Contains error codes that shall be
    communicated to client part of engine
    """
    SUCCESS = 0
    # values from 1 up to 200 are reserved
    # for answers of business handlers
    DOCMAKER_ERROR = 200

    # values from 201 up to 255 are reserved
    # for answers of controller factory mechanism
    MOD_BUSINESS_NOT_LOADED = 201
    MOD_BUSINESS_UNEXPECTED_FAIL = 202
    MODE_NOT_SUPPORTED = 203
    BUFF_INCOMPLETE = 204

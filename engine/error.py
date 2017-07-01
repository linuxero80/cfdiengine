import enum


class ErrorCode(enum.Enum):
    """
    Contains error codes that shall be
    communicated to client part of engine
    """
    SUCCESS = 0
    # values from 1 up to 200 are reserved
    # for answers of business handlers
    ETL_ISSUES = 197          # ETL means extract, transform, and load
    REQUEST_INCOMPLETE = 198  # Denotes a missing value in request
    DOCMAKER_ERROR = 199      # Problems related to docmaker stuff
    THIRD_PARTY_ISSUES = 200  # Lack interacting with third party entities

    # values from 201 up to 255 are reserved
    # for answers of engine mechanism
    MOD_BUSINESS_NOT_LOADED = 201
    MOD_BUSINESS_UNEXPECTED_FAIL = 202
    MODE_NOT_SUPPORTED = 203
    BUFF_INCOMPLETE = 204

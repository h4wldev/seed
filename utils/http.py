import enum


class HTTPMethod(enum.Enum):
    GET = 'get'
    HEAD = 'head'
    POST = 'post'
    PUT = 'put'
    DELETE = 'delete'
    OPTIONS = 'options'
    TRACE = 'trace'
    PATCH = 'patch'


class HTTPStatusType(enum.Enum):
    INFORMATIONAL = 1
    SUCCESS = 2
    REDIRECT = 3
    CLIENT_ERROR = 4
    SERVER_ERROR = 5


class HTTPStatusCode(enum.Enum):
    CONTINUE = 100
    SWITCHING_PROTOCOLS = 101
    PROCESSING = 102
    OK = 200
    CREATED = 201
    ACCEPTED = 202
    NON_AUTHORITATIVE_INFORMATION = 203
    NO_CONTENT = 204
    RESET_CONTENT = 205
    PARTIAL_CONTENT = 206
    MULTI_STATUS = 207
    ALREADY_REPORTED = 208
    IM_USED = 226
    MULTIPLE_CHOICES = 300
    MOVED_PERMANENTLY = 301
    FOUND = 302
    SEE_OTHER = 303
    NOT_MODIFIED = 304
    USE_PROXY = 305
    TEMPORARY_REDIRECT = 307
    PERMANENT_REDIRECT = 308
    BAD_REQUEST = 400
    UNAUTHORIZED = 401
    PAYMENT_REQUIRED = 402
    FORBIDDEN = 403
    NOT_FOUND = 404
    METHOD_NOT_ALLOWED = 405
    NOT_ACCEPTABLE = 406
    PROXY_AUTHENTICATION_REQUIRED = 407
    REQUEST_TIMEOUT = 408
    CONFLICT = 409
    GONE = 410
    LENGTH_REQUIRED = 411
    PRECONDITION_FAILED = 412
    REQUEST_ENTITY_TOO_LARGE = 413
    REQUEST_URI_TOO_LONG = 414
    UNSUPPORTED_MEDIA_TYPE = 415
    REQUESTED_RANGE_NOT_SATISFIABLE = 416
    EXPECTATION_FAILED = 417
    MISDIRECTED_REQUEST = 421
    UNPROCESSABLE_ENTITY = 422
    LOCKED = 423
    FAILED_DEPENDENCY = 424
    UPGRADE_REQUIRED = 426
    PRECONDITION_REQUIRED = 428
    TOO_MANY_REQUESTS = 429
    REQUEST_HEADER_FIELDS_TOO_LARGE = 431
    INTERNAL_SERVER_ERROR = 500
    NOT_IMPLEMENTED = 501
    BAD_GATEWAY = 502
    SERVICE_UNAVAILABLE = 503
    GATEWAY_TIMEOUT = 504
    HTTP_VERSION_NOT_SUPPORTED = 505
    VARIANT_ALSO_NEGOTIATES = 506
    INSUFFICIENT_STORAGE = 507
    LOOP_DETECTED = 508
    NOT_EXTENDED = 509
    NETWORK_AUTHENTICATION_REQUIRED = 511

    def __str__(self) -> str:
        return f'{self.name} ({self.value})'

    def get_type(self) -> HTTPStatusType:
        if self.is_informational():
            return HTTPStatusType.INFORMATIONAL
        elif self.is_success():
            return HTTPStatusType.SUCCESS
        elif self.is_redirect():
            return HTTPStatusType.REDIRECT
        elif self.is_client_error():
            return HTTPStatusType.CLIENT_ERROR
        elif self.is_server_error():
            return HTTPStatusType.SERVER_ERROR

    def is_informational(self) -> bool:
        return 100 <= self.value <= 199

    def is_success(self) -> bool:
        return 200 <= self.value <= 299

    def is_redirect(self) -> bool:
        return 300 <= self.value <= 399

    def is_client_error(self) -> bool:
        return 400 <= self.value <= 499

    def is_server_error(self) -> bool:
        return 500 <= self.value <= 599

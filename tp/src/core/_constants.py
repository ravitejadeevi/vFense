class CommonKeys():
    YES = 'yes'
    NO = 'no'
    COUNT = 'count'
    DETAILS = 'details'
    REDUCTION = 'reduction'
    USERNAME = 'username'
    PASSWORD = 'password'
    USER = 'user'
    URI = 'uri'
    METHOD = 'method'
    RESPONSE_URI = 'response_uri'
    RESPONSE_METHOD = 'request_method'

class DefaultStringLength():
    CUSTOMER_NAME = 36
    GROUP_NAME = 36
    USER_NAME = 24

class HTTPMethods():
    PUT = 'put'
    POST = 'post'
    DELETE = 'delete'
    GET = 'get'
    HEAD = 'head'

class CPUThrottleValues():
    IDLE = 'idle'
    BELOW_NORMAL = 'below_normal'
    NORMAL = 'normal'
    ABOVE_NORMAL = 'above_normal'
    HIGH = 'high'
    VALID_VALUES = (IDLE, BELOW_NORMAL, NORMAL, ABOVE_NORMAL, HIGH)

class RebootValues():
    NONE = 'none' #Do not reboot
    NEEDED = 'needed' #Reboot only if the system is asking for a reboot
    FORCE = 'force'   #Force the reboot
    VALID_VALUES = (NONE, NEEDED, FORCE)

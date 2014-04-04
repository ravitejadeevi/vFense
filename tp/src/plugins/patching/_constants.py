class CommonAppKeys():
    CustomerName = 'customer_name'
    Id = 'id'
    APP_ID = 'app_id'
    APP_NAME = 'app_name'
    APP_URIS = 'app_uris'
    AGENTID = 'agent_id'
    COUNT = 'count'
    AGENT_COUNT = 'agent_count'
    AGENTS = 'agents'
    STATUS = 'status'
    NAME = 'name'
    VERSION = 'version'
    INSTALLED = 'installed'
    AVAILABLE = 'available'
    PENDING = 'pending'
    SOFTWAREINVENTORY = 'Software Inventory'
    OS = 'OS'
    CUSTOM = 'Custom'
    SUPPORTED = 'Supported'
    AGENT_UPDATES = 'Agent Updates'
    ValidPackageStatuses = (INSTALLED, AVAILABLE, PENDING)
    YES = 'yes'
    NO = 'no'
    ValidHiddenVals = (YES, NO)

class CommonFileKeys():
    PKG_NAME = 'file_name'
    PKG_SIZE = 'file_size'
    PKG_URI = 'file_uri'
    FILE_URIS = 'file_uris'
    PKG_HASH = 'file_hash'
    PKG_URIS = 'uris'
    PKG_FILEDATA = 'file_data'
    PKG_CLI_OPTIONS = 'cli_options'

class CommonSeverityKeys():
    CRITICAL = 'Critical'
    OPTIONAL = 'Optional'
    RECOMMENDED = 'Recommended'
    ValidRvSeverities = (CRITICAL, RECOMMENDED, OPTIONAL)


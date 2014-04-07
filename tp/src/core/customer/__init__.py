class CustomerCollections():
    Customers = 'customers'
    CustomersPerUser = 'customers_per_user'

class CustomerKeys():
    CustomerName = 'customer_name'
    Properties = 'properties'
    NetThrottle = 'net_throttle'
    CpuThrottle = 'cpu_throttle'
    PackageUrl = 'package_download_url_base'
    ServerQueueTTL = 'server_queue_ttl' # in minutes
    AgentQueueTTL = 'agent_queue_ttl' # in minutes
    Users = 'users' #Mapped Keys
    Groups = 'groups' #Mapped Keys

class CustomerPerUserKeys():
    CustomerName = 'customer_name'
    UserName = 'user_name'
    Id = 'id'

class CustomerPerUserIndexes():
    CustomerName = 'customer_name'
    UserName = 'user_name'

import logging
import re

from vFense.core._constants import CPUThrottleValues, DefaultStringLength
from vFense.core._db import retrieve_object
from vFense.core.customer import *
from vFense.core.customer._constants import DefaultCustomers
from vFense.core.user import *
from vFense.core.user._constants import DefaultUser
from vFense.core.customer._db import insert_customer, fetch_customer, \
    insert_user_per_customer, delete_user_in_customers , delete_customer, \
    users_exists_in_customer, update_customer, fetch_users_for_customer, \
    fetch_properties_for_all_customers, fetch_properties_for_customer, \
    users_exists_in_customers, delete_customers

from vFense.core.decorators import results_message, time_it
from vFense.errorz.status_codes import *
from vFense.errorz._constants import ApiResultKeys

logging.config.fileConfig('/opt/TopPatch/conf/logging.config')
logger = logging.getLogger('rvapi')


@time_it
def get_customer(customer_name, keys_to_pluck=None):
    """Retrieve customer information.
    Args:
        customer_name (str):  Name of the customer.

    Kwargs:
        keys_to_pluck (list):  list of keys you want to retreive from the db.

    Basic Usage:
        >>> from vFense.customer.customers get_customer
        >>> customer_name = 'default'
        >>> get_customer(customer_name)

    Return:
        Dictionary of customer properties.
        {
            u'cpu_throttle': u'normal',
            u'package_download_url_base': u'http: //10.0.0.21/packages/',
            u'operation_ttl': 10,
            u'net_throttle': 0,
            u'customer_name': u'default'
        }
    """
    customer_data = {}
    if keys_to_pluck:
        customer_data = fetch_customer(customer_name, keys_to_pluck)
    else:
        customer_data = fetch_customer(customer_name)

    return(customer_data)


@time_it
def get_customer_property(customer_name, customer_property):
    """Retrieve customer property.
    Args:
        customer_name (str):  Name of the customer.

    Kwargs:
        customer_property (str): Property you want to retrieve.

    Basic Usage:
        >>> from vFense.customer.customers get_customer_property
        >>> customer_name = 'default'
        >>> customer_property = 'operation_ttl'
        >>> get_customer(customer_name)

    Return:
        String
    """
    customer_data = fetch_customer(customer_name)
    customer_key = None
    if customer_data:
        customer_key = customer_data.get(customer_property)

    return(customer_key)


@time_it
def get_customers(match=None, keys_to_pluck=None):
    """Retrieve all customers or just customers based on regular expressions
    Kwargs:
        match (str): Regular expression of the customer name
            you are searching for.
        keys_to_pluck (array): list of keys you want to retreive from the db.

    Returns:
        Returns a List of customers

    Basic Usage::
        >>> from vFense.customer.customers import get_customers
        >>> get_customers()

    Return:
        List of dictionaries of customer properties.
        [
            {
                u'cpu_throttle': u'normal',
                u'package_download_url_base': u'http: //10.0.0.21/packages/',
                u'operation_ttl': 10,
                u'net_throttle': 0,
                u'customer_name': u'default'
            },
            {
                u'cpu_throttle': u'normal',
                u'package_download_url_base': u'http: //10.0.0.21/packages/',
                u'operation_ttl': 10,
                u'net_throttle': 0,
                u'customer_name': u'TopPatch'
            }
        ]
    """
    customer_data = {}
    if match and keys_to_pluck:
        customer_data = fetch_customers(match, keys_to_pluck)

    elif match and not keys_to_pluck:
        customer_data = fetch_customers(match)

    elif not match and keys_to_pluck:
        customer_data = fetch_customers(keys_to_pluck)

    elif not match and not keys_to_pluck:
        customer_data = fetch_customers()

    return(customer_data)


@time_it
def get_properties_for_customer(customer_name):
    """Retrieve a customer and all its properties
    Args:
        customer_name (str): Name of the customer

    Returns:
        Returns a Dictionary of customers

    Basic Usage::
        >>> from vFense.customer.customer import get_properties_for_customer
        >>> get_properties_for_customer(customer_name)

    Return:
        Dictionary of customer properties.
    """
    data = fetch_properties_for_customer(customer_name)
    return(data)


@time_it
def get_properties_for_all_customers(username=None):
    """Retrieve all customers or retrieve all customers that user has
        access to.
    Kwargs:
        user_name (str): Name of the username, w

    Returns:
        Returns a List of customers

    Basic Usage::
        >>> from vFense.customer.customer import get_properties_for_all_customers
        >>> fetch_properties_for_all_customers()

    Return:
        List of customer properties.
        [
            {
                u'cpu_throttle': u'normal',
                u'package_download_url_base': u'http: //10.0.0.21/packages/',
                u'operation_ttl': 10,
                u'net_throttle': 0,
                u'customer_name': u'default'
            },
            {
                u'cpu_throttle': u'normal',
                u'package_download_url_base': u'http: //10.0.0.21/packages/',
                u'operation_ttl': 10,
                u'net_throttle': 0,
                u'customer_name': u'TopPatch'
            }
        ]
    """
    data = fetch_properties_for_all_customers(username)
    return(data)

def _validate_customer_data(**kwargs):
    data_validated = False
    if kwargs.get(CustomerKeys.NetThrottle):
        valid_net_throttle = True
        net_throttle = kwargs.get(CustomerKeys.NetThrottle)
        if not isinstance(net_throttle, int):
            try:
                net_throttle = int(net_throttle)

            except ValueError:
                valid_net_throttle = False

        return(valid_net_throttle)

    if kwargs.get(CustomerKeys.CpuThrottle):
        cpu_throttle = kwargs.get(CustomerKeys.CpuThrottle)
        valid_cpu_throttle = cpu_throttle in CPUThrottleValues.VALID_VALUES

        return(valid_cpu_throttle)

    if kwargs.get(CustomerKeys.PackageUrl):
        valid_pkg_url = False
        pkg_url = kwargs.get(CustomerKeys.PackageUrl)
        if re.search(r'^http(s)?://', pkg_url):
            valid_pkg_url = True

        return(valid_pkg_url)

    if kwargs.get(CustomerKeys.ServerQueueTTL):
        valid_operation_ttl = True
        operation_queue_ttl = kwargs.get(CustomerKeys.ServerQueueTTL)
        if not isinstance(operation_queue_ttl, int):
            try:
                operation_queue_ttl = int(operation_queue_ttl)

            except ValueError:
                valid_operation_ttl = False

        return(valid_operation_ttl)

    if kwargs.get(CustomerKeys.AgentQueueTTL):
        valid_operation_ttl = True
        operation_queue_ttl = kwargs.get(CustomerKeys.AgentQueueTTL)
        if not isinstance(operation_queue_ttl, int):
            try:
                operation_queue_ttl = int(operation_queue_ttl)

            except ValueError:
                valid_operation_ttl = False

        return(valid_operation_ttl)


    return(data_validated)


@time_it
def validate_customer_names(customer_names):
    """Validate a list if customer names.
    Args:
        customer_names (list): List of customer names.

    Basic Usage:
        >>> from vFense.customer.customers import validate_customer_names
        >>> customer_names = ['default', 'TOpPatch']
        >>> validate_customer_names(customer_names)

    Return:
        Tuple - (Boolean, [valid list], [invalid list])
        (False, ['default'], ['TOpPatch'])
    """
    validated = True
    invalid_names = []
    valid_names = []
    if isinstance(customer_names, list):
        for customer_name in customer_names:
            if get_customer(customer_name):
                valid_names.append(customer_name)
            else:
                invalid_names.append(customer_name)
                validated = False

    return(validated, valid_names, invalid_names)


@time_it
@results_message
def add_user_to_customers(
    username, customer_names,
    user_name=None, uri=None, method=None
    ):
    """Add a multiple customers to a user
    Args:
        username (str):  Name of the user already in vFense.
        customer_names (list): List of customer names,
            this user will be added to.

    Kwargs:
        user_name (str): The name of the user who called this function.
        uri (str): The uri that was used to call this function.
        method (str): The HTTP methos that was used to call this function.

    Basic Usage:
        >>> from vFense.core.customer.customer import add_user_to_customers
        >>> username = 'admin'
        >>> customer_names = ['default', 'TopPatch', 'vFense']
        >>> add_user_to_customers(username, customer_names)

    Returns:
        Dictionary of the status of the operation.
        {
            'uri': None,
            'rv_status_code': 1017,
            'http_method': None,
            'http_status': 200,
            'message': "None - add_user_to_customers - customer names existed 'default', 'TopPatch', 'vFense' unchanged",
            'data': []

        }
    """
    if isinstance(customer_names, str):
        customer_names = customer_names.split(',')

    customers_are_valid = validate_customer_names(customer_names)
    results = None
    user_exist = retrieve_object(username, UserCollections.Users)
    data_list = []
    status = add_user_to_customers.func_name + ' - '
    msg = ''
    status_code = 0
    generic_status_code = 0
    vfense_status_code = 0
    generated_ids = []
    if customers_are_valid[0]:
        data_list = []
        for customer_name in customer_names:
            if not users_exists_in_customer(username, customer_name):
                data_to_add = (
                    {
                        CustomerPerUserKeys.CustomerName: customer_name,
                        CustomerPerUserKeys.UserName: username,
                    }
                )
                data_list.append(data_to_add)

        if user_exist and data_list:
            status_code, object_count, error, generated_ids = (
                insert_user_per_customer(data_list)
            )
            if status_code == DbCodes.Inserted:
                msg = (
                    'user %s added to %s' % (
                        username, ' and '.join(customer_names)
                    )
                )
                generic_status_code = GenericCodes.ObjectCreated
                vfense_status_code = CustomerCodes.CustomersAddedToUser

        elif user_exist and not data_list:
            status_code = DbCodes.Unchanged
            msg = 'customer names existed for user %s' % (username)
            generic_status_code = GenericCodes.ObjectExists
            vfense_status_code = CustomerFailureCodes.UsersExistForCustomer

        elif not user_exist:
            status_code = DbCodes.Errors
            msg = 'User name is invalid: %s' % (username)
            generic_status_code = GenericCodes.InvalidId
            vfense_status_code = UserFailureCodes.UserNameDoesNotExists

    elif not customers_are_valid[0]:
        status_code = DbCodes.Errors
        msg = (
            'Customer names are invalid: %s' % (
                ' and '.join(customers_are_valid[2])
            )
        )
        generic_status_code = GenericCodes.InvalidId
        vfense_status_code = CustomerFailureCodes.InvalidCustomerName

    results = {
        ApiResultKeys.DB_STATUS_CODE: status_code,
        ApiResultKeys.GENERIC_STATUS_CODE: generic_status_code,
        ApiResultKeys.VFENSE_STATUS_CODE: vfense_status_code,
        ApiResultKeys.GENERATED_IDS: generated_ids,
        ApiResultKeys.MESSAGE: status + msg,
        ApiResultKeys.DATA: [],
        ApiResultKeys.USERNAME: user_name,
        ApiResultKeys.URI: uri,
        ApiResultKeys.HTTP_METHOD: method
    }

    return(results)


@time_it
@results_message
def create_customer(
    customer_name, username=None,
    http_application_url_location=None,
    net_throttle=0, cpu_throttle='normal',
    server_queue_ttl=10, agent_queue_ttl=10,
    init=False, user_name=None, uri=None, method=None
    ):
    """Create a new customer inside of vFense
    Args:
        customer_name (str): Name of the customer you are creating.
            The customer name can be a total length of 36 characters,
            with a combination of characters, numbers, - _ and spaces.

    Kwargs:
        username (str): Name of the user that you are adding to this customer.
            Default=None
            If init is set to True, then it can stay as None
            else, then a valid user must be passed
        http_application_url_location (str): This is the http url from
            which the agents will download its applications from.
            Default=Use the same url, that the default customer uses
        net_throttle (int): Bandwidth throttling is calculated in kb.
            Default=0 (0, means not to throttle)
        cpu_throttle (int): Throttle how much CPU is being used
            during any operation.
            Default=normal 
            possbile values (idle, below_normal, normal, above_noraml, high)
        server_queue_ttl (int):minutes until an operation is
            considered expired inside the server queue
            Default=10
        agent_queue_ttl (int):minutes until an operation is
            considered expired inside the agent queue
            Default=10
        init (boolean): Create the customer, without adding a user into it.
            Default=False
        user_name (str): The name of the user who called this function.
        uri (str): The uri that was used to call this function.
        method (str): The HTTP methos that was used to call this function.

    Basic Usage:
        >>> from vFense.customer.customers import create_customer
        >>> customer_name = 'vFense'
        >>> username = 'api_user'
        >>> http_application_url_location='https://10.0.0.16/packages/'
        >>> create_customer(
                customer_name, api_user,
                http_application_url_location
            )

    Return:
        Dictionary of the status of the operation.
        {
            'uri': None,
            'rv_status_code': 1010,
            'http_method': None,
            'http_status': 200,
            'message': 'api_user - customer vFense was created',
            'data': {
                'cpu_throttle': 'normal',
                'package_download_url_base': 'https: //10.0.0.21/packages/',
                'server_queue_ttl': 10,
                'agent_queue_ttl': 10,
                'net_throttle': 0,
                'customer_name': 'vFense'
            }
        }
    """
    customer_exist = get_customer(customer_name)
    status = create_customer.func_name + ' - '
    msg = ''
    status_code = 0
    generic_status_code = 0
    vfense_status_code = 0
    data = {}
    generated_ids = []
    valid_net_throttle = True
    valid_server_queue_ttl = True
    valid_agent_queue_ttl = True
    valid_cpu_throttle = cpu_throttle in CPUThrottleValues.VALID_VALUES
    valid_customer_name = (
        re.search('((?:[A-Za-z0-9_-](?!\s+")|\s(?!\s*")){1,36})', customer_name)
    )
    valid_customer_length = (
        len(customer_name) <= DefaultStringLength.CUSTOMER_NAME
    )
    if not isinstance(net_throttle, int):
        try:
            net_throttle = int(net_throttle)

        except ValueError:
            valid_net_throttle = False

    if not isinstance(server_queue_ttl, int):
        try:
            server_queue_ttl = int(server_queue_ttl)

        except ValueError:
            valid_server_queue_ttl = False

    if not isinstance(agent_queue_ttl, int):
        try:
            agent_queue_ttl = int(agent_queue_ttl)

        except ValueError:
            valid_agent_queue_ttl = False

    if (not customer_exist and valid_server_queue_ttl and
        valid_agent_queue_ttl and
        valid_net_throttle and valid_cpu_throttle and
        valid_customer_name and valid_customer_length):

        if not http_application_url_location:
            http_application_url_location = (
                get_customer(
                    DefaultCustomers.DEFAULT,
                    [CustomerKeys.PackageUrl]
                ).get(CustomerKeys.PackageUrl)
            )

        data = {
            CustomerKeys.CustomerName: customer_name,
            CustomerKeys.PackageUrl: http_application_url_location,
            CustomerKeys.NetThrottle: net_throttle,
            CustomerKeys.CpuThrottle: cpu_throttle,
            CustomerKeys.ServerQueueTTL: server_queue_ttl,
            CustomerKeys.AgentQueueTTL: agent_queue_ttl,
        }
        object_status, object_count, error, generated_ids = (
            insert_customer(data)
        )
        if object_status == DbCodes.Inserted:
            generated_ids.append(customer_name)
            msg = 'customer %s created - ' % (customer_name)
            generic_status_code = GenericCodes.ObjectCreated
            vfense_status_code = CustomerCodes.CustomerCreated

        if object_status == DbCodes.Inserted and not init and username:
            add_user_to_customers(
                username, customer_name, user_name, uri, method
            )

            if username != DefaultUser.ADMIN:
                add_user_to_customers(
                    DefaultUser.ADMIN, customer_name, user_name, uri, method
                )

        #The admin user should be part of every group
        elif object_status == DbCodes.Inserted and username != DefaultUser.ADMIN:
            admin_exist = (
                retrieve_object(
                    DefaultUser.ADMIN, UserCollections.Users
                )
            )
            
            if admin_exist:
                add_user_to_customers(
                    DefaultUser.ADMIN, customer_name, user_name, uri, method
                )


    elif customer_exist:
        status_code = DbCodes.Unchanged
        msg = 'customer_name %s already exists' % (customer_name)
        generic_status_code = GenericCodes.ObjectExists
        vfense_status_code = CustomerFailureCodes.CustomerExists

    elif not valid_net_throttle:
        status_code = DbCodes.Errors
        msg = (
            'network throttle was not given a valid integer :%s' %
            (net_throttle)
        )
        generic_status_code = GenericCodes.InvalidId
        vfense_status_code = CustomerFailureCodes.InvalidNetworkThrottle

    elif not valid_cpu_throttle:
        status_code = DbCodes.Errors
        msg = (
            'cpu throttle was not given a valid value :%s' %
            (cpu_throttle)
        )
        generic_status_code = GenericCodes.InvalidId
        vfense_status_code = CustomerFailureCodes.InvalidCpuThrottle

    elif not valid_server_queue_ttl:
        status_code = DbCodes.Errors
        msg = (
            'server queue ttl was not given a valid value :%s' %
            (server_queue_ttl)
        )
        generic_status_code = GenericCodes.InvalidId
        vfense_status_code = CustomerFailureCodes.InvalidOperationTTL

    elif not valid_agent_queue_ttl:
        status_code = DbCodes.Errors
        msg = (
            'agent queue ttl was not given a valid value :%s' %
            (agent_queue_ttl)
        )
        generic_status_code = GenericCodes.InvalidId
        vfense_status_code = CustomerFailureCodes.InvalidOperationTTL

    elif not valid_customer_length or not valid_customer_name:
        status_code = DbCodes.Errors
        msg = (
            'customer name is not within the 36 character range '+
            'or contains unsupported characters :%s' %
            (customer_name)
        )
        generic_status_code = GenericCodes.InvalidId
        vfense_status_code = CustomerFailureCodes.InvalidCustomerName

    results = {
        ApiResultKeys.DB_STATUS_CODE: status_code,
        ApiResultKeys.GENERIC_STATUS_CODE: generic_status_code,
        ApiResultKeys.VFENSE_STATUS_CODE: vfense_status_code,
        ApiResultKeys.MESSAGE: status + msg,
        ApiResultKeys.DATA: [data],
        ApiResultKeys.USERNAME: user_name,
        ApiResultKeys.URI: uri,
        ApiResultKeys.HTTP_METHOD: method
    }

    return(results)


@time_it
@results_message
def edit_customer(customer_name, **kwargs):
    """ Edit the properties of a customer. 
    Args:
        customer_name (str): Name  of the customer you are editing.

    Kwargs:
        http_application_url_location (str): This is the http url from
            which the agents will download its applications from.
        net_throttle (int): Bandwidth throttling is calculated in kb.
        cpu_throttle (int): Throttle how much CPU is being used
            during any operation.
            possbile values (idle, below_normal, normal, above_noraml, high)
        server_queue_ttl (int):minutes until an operation is
            considered expired inside the server queue
        agent_queue_ttl (int):minutes until an operation is
            considered expired inside the agent queue
        user_name (str): The name of the user who called this function.
        uri (str): The uri that was used to call this function.
        method (str): The HTTP methos that was used to call this function.

    Basic Usage:
        >>> from vFense.core.customer.customers edit_customer
        >>> customer_name = 'agent_api'
        >>> edit_customer(customer_name, server_queue_ttl=5)

    Returns:
        Dictionary of the status of the operation.
        {
            'uri': None,
            'rv_status_code': 1008,
            'http_method': None,
            'http_status': 200,
            'message': 'None - customer modified - default was updated',
            'data': {
                'server_queue_ttl': 5
            }
        }
    """

    if not kwargs.get(ApiResultKeys.USERNAME):
        user_name = None
    else:
        user_name = kwargs.pop(ApiResultKeys.USERNAME)

    if not kwargs.get(ApiResultKeys.URI):
        uri = None
    else:
        uri = kwargs.pop(ApiResultKeys.URI)

    if not kwargs.get(ApiResultKeys.HTTP_METHOD):
        method = None
    else:
        method = kwargs.pop(ApiResultKeys.HTTP_METHOD)

    status = edit_customer.func_name + ' - '

    try:
        invalid_data = []
        for key, val in kwargs.items():
            if not _validate_customer_data(**{key:val}):
                invalid_data.append({key:val})

        if invalid_data:
            msg = (
                'data was invalid for customer %s: %s- ' %
                (customer_name, invalid_data)
            )
            status_code = DbCodes.Unchanged
            generic_status_code = GenericCodes.ObjectUnchanged
            vfense_status_code = CustomerCodes.CustomerUnchanged

        else:
            status_code, count, error, generated_ids = (
                update_customer(customer_name, kwargs)
            )
            if status_code == DbCodes.Replaced:
                msg = 'customer %s updated - ' % (customer_name)
                generic_status_code = GenericCodes.ObjectUpdated
                vfense_status_code = CustomerCodes.CustomerUpdated

            elif status_code == DbCodes.Unchanged:
                msg = 'customer %s unchanged - ' % (customer_name)
                generic_status_code = GenericCodes.ObjectUnchanged
                vfense_status_code = CustomerCodes.CustomerUnchanged

            elif status_code == DbCodes.Skipped:
                msg = 'customer %s does not exist - ' % (customer_name)
                generic_status_code = GenericCodes.Invalid
                vfense_status_code = CustomerFailureCodes.InvalidCustomerName

        results = {
            ApiResultKeys.DB_STATUS_CODE: status_code,
            ApiResultKeys.GENERIC_STATUS_CODE: generic_status_code,
            ApiResultKeys.VFENSE_STATUS_CODE: vfense_status_code,
            ApiResultKeys.MESSAGE: status + msg,
            ApiResultKeys.DATA: [kwargs],
            ApiResultKeys.USERNAME: user_name,
            ApiResultKeys.URI: uri,
            ApiResultKeys.HTTP_METHOD: method
        }

    except Exception as e:
        logger.exception(e)
        msg = 'Failed to modify customer %s: %s' % (customer_name, str(e))
        status_code = DbCodes.Errors
        generic_status_code = GenericFailureCodes.FailedToUpdateObject
        vfense_status_code = CustomerFailureCodes.FailedToRemoveCustomer

        results = {
            ApiResultKeys.DB_STATUS_CODE: status_code,
            ApiResultKeys.GENERIC_STATUS_CODE: generic_status_code,
            ApiResultKeys.VFENSE_STATUS_CODE: vfense_status_code,
            ApiResultKeys.MESSAGE: status + msg,
            ApiResultKeys.DATA: [kwargs],
            ApiResultKeys.USERNAME: user_name,
            ApiResultKeys.URI: uri,
            ApiResultKeys.HTTP_METHOD: method
        }

    return(results)


@time_it
@results_message
def remove_customers_from_user(
    username, customer_names=None,
    user_name=None, uri=None, method=None
    ):
    """Remove a customer from a user
    Args:
        username (str): Username of the user, you are
            removing the customer from.

    Kwargs:
        customer_names (list): List of customer_names,
            you want to remove from this user
        user_name (str): The name of the user who called this function.
        uri (str): The uri that was used to call this function.
        method (str): The HTTP methos that was used to call this function.

    Basic Usage:
        >>> from vFense.customer.customers remove_customers_from_user
        >>> username = 'agent_api'
        >>> remove_customers_from_user(username)

    Return:
        Dictionary of the status of the operation.
    {
        'rv_status_code': 1004,
        'message': 'None - remove_customers_from_user - removed customers from user alien: TopPatch and vFense does not exist',
        'http_method': None,
        'uri': None,
        'http_status': 409
    }
    """
    status = remove_customers_from_user.func_name + ' - '
    try:
        status_code, count, errors, generated_ids = (
            delete_user_in_customers(username, customer_names)
        )
        if status_code == DbCodes.Deleted:
            msg = 'removed customers from user %s' % (username)
            generic_status_code = GenericCodes.ObjectDeleted
            vfense_status_code = CustomerCodes.CustomersRemovedFromUser

        elif status_code == DbCodes.Skipped:
            msg = 'invalid customer name or invalid username'
            generic_status_code = GenericCodes.InvalidId
            vfense_status_code = CustomerFailureCodes.InvalidCustomerName

        elif status_code == DbCodes.DoesntExist:
            msg = 'customer name or username does not exist'
            generic_status_code = GenericCodes.DoesNotExists
            vfense_status_code = CustomerFailureCodes.UsersDoNotExistForCustomer

        results = {
            ApiResultKeys.DB_STATUS_CODE: status_code,
            ApiResultKeys.GENERIC_STATUS_CODE: generic_status_code,
            ApiResultKeys.VFENSE_STATUS_CODE: vfense_status_code,
            ApiResultKeys.MESSAGE: status + msg,
            ApiResultKeys.DATA: [],
            ApiResultKeys.USERNAME: user_name,
            ApiResultKeys.URI: uri,
            ApiResultKeys.HTTP_METHOD: method
        }

    except Exception as e:
        logger.exception(e)
        msg = (
            'Failed to remove customers from user %s: %s' % 
            (username, str(e))
        )
        status_code = DbCodes.Errors
        generic_status_code = GenericFailureCodes.FailedToDeleteObject
        vfense_status_code = CustomerFailureCodes.FailedToRemoveCustomer

        results = {
            ApiResultKeys.DB_STATUS_CODE: status_code,
            ApiResultKeys.GENERIC_STATUS_CODE: generic_status_code,
            ApiResultKeys.VFENSE_STATUS_CODE: vfense_status_code,
            ApiResultKeys.MESSAGE: status + msg,
            ApiResultKeys.DATA: [],
            ApiResultKeys.USERNAME: user_name,
            ApiResultKeys.URI: uri,
            ApiResultKeys.HTTP_METHOD: method
        }

    return(results)


@time_it
@results_message
def remove_customer(customer_name, user_name=None, uri=None, method=None):
    """ Remove a customer from vFense
    Args:
        customer_name: Name of the customer you are removing.

    Kwargs:
        user_name (str): The name of the user who called this function.
        uri (str): The uri that was used to call this function.
        method (str): The HTTP methos that was used to call this function.

    Basic Usage:
        >>> from vFense.core.customer.customers remove_customer
        >>> customer_name = 'nyc'
        >>> remove_customer(customer_name)

    Return:
        Dictionary of the status of the operation.
        {
            'rv_status_code': 1012,
            'message': 'None - remove_customer - vFense was deleted',
            'http_method': None,
            'uri': None,
            'http_status': 200

        }
    """
    status = remove_customer.func_name + ' - '
    status_code = 0
    generic_status_code = 0
    vfense_status_code = 0
    customers_deleted = []
    try:
        customer_exist = get_customer(customer_name)
        users_exist = fetch_users_for_customer(customer_name)
        default_in_list = DefaultCustomers.DEFAULT == customer_name

        if customer_exist and not users_exist and not default_in_list:
            status_code, count, errors, generated_ids = (
                delete_customer(customer_name)
            )

            if status_code == DbCodes.Deleted:
                msg = 'customer %s removed' % customer_name
                generic_status_code = GenericCodes.ObjectDeleted
                vfense_status_code = CustomerCodes.CustomerDeleted
                customers_deleted.append(customer_name)


        elif customer_exist and users_exist and not default_in_list:
            msg = (
                'users still exist for customer %s' % customer_name
            )
            status_code = DbCodes.Unchanged
            generic_status_code = GenericFailureCodes.FailedToDeleteObject
            vfense_status_code = CustomerFailureCodes.UsersExistForCustomer

        elif default_in_list:
            msg = 'Can not delete the default customer'
            status_code = DbCodes.Unchanged
            generic_status_code = GenericFailureCodes.FailedToDeleteObject
            vfense_status_code = CustomerFailureCodes.CantDeleteDefaultCustomer

        else:
            msg = 'customer %s does not exist' % (customer_name)
            status_code = DbCodes.Skipped
            generic_status_code = GenericCodes.InvalidId
            vfense_status_code = CustomerFailureCodes.InvalidCustomerName

        results = {
            ApiResultKeys.DB_STATUS_CODE: status_code,
            ApiResultKeys.GENERIC_STATUS_CODE: generic_status_code,
            ApiResultKeys.VFENSE_STATUS_CODE: vfense_status_code,
            ApiResultKeys.DELETED_IDS: customers_deleted,
            ApiResultKeys.MESSAGE: status + msg,
            ApiResultKeys.DATA: [],
            ApiResultKeys.USERNAME: user_name,
            ApiResultKeys.URI: uri,
            ApiResultKeys.HTTP_METHOD: method
        }

    except Exception as e:
        logger.exception(e)
        msg = 'Failed to remove customer %s: %s' % (customer_name, str(e))
        status_code = DbCodes.Errors
        generic_status_code = GenericFailureCodes.FailedToDeleteObject
        vfense_status_code = CustomerFailureCodes.FailedToRemoveCustomer

        results = {
            ApiResultKeys.DB_STATUS_CODE: status_code,
            ApiResultKeys.GENERIC_STATUS_CODE: generic_status_code,
            ApiResultKeys.VFENSE_STATUS_CODE: vfense_status_code,
            ApiResultKeys.DELETED_IDS: customers_deleted,
            ApiResultKeys.MESSAGE: status + msg,
            ApiResultKeys.DATA: [],
            ApiResultKeys.USERNAME: user_name,
            ApiResultKeys.URI: uri,
            ApiResultKeys.HTTP_METHOD: method
        }

    return(results)


@time_it
@results_message
def remove_customers(customer_names, user_name=None, uri=None, method=None):
    """ Remove a customer from vFense
    Args:
        customer_names: Name of the customers you are removing.

    Kwargs:
        user_name (str): The name of the user who called this function.
        uri (str): The uri that was used to call this function.
        method (str): The HTTP methos that was used to call this function.

    Basic Usage:
        >>> from vFense.core.customer.customers remove_customers
        >>> customer_names = ['nyc', 'foo']
        >>> remove_customers(customer_names)

    Return:
        Dictionary of the status of the operation.
        {
            'rv_status_code': 1012,
            'message': 'None - remove_customer - vFense was deleted',
            'http_method': None,
            'uri': None,
            'http_status': 200

        }
    """
    status = remove_customer.func_name + ' - '
    status_code = 0
    generic_status_code = 0
    vfense_status_code = 0
    customers_deleted = []
    try:
        customers_are_valid = validate_customer_names(customer_names)
        users_exist = users_exists_in_customers(customer_names)
        default_in_list = DefaultCustomers.DEFAULT in customer_names
        if customers_are_valid[0] and not users_exist[0] and not default_in_list:
            status_code, count, errors, generated_ids = (
                delete_customers(customer_names)
            )
            if status_code == DbCodes.Deleted:
                msg = 'customers %s removed' % customer_names
                generic_status_code = GenericCodes.ObjectDeleted
                vfense_status_code = CustomerCodes.CustomerDeleted
                customers_deleted = customer_names


        elif users_exist[0] and not default_in_list:
            msg = (
                'users still exist for customer %s' % 
                (' and '.join(users_exist[1]))
            )
            status_code = DbCodes.Unchanged
            generic_status_code = GenericFailureCodes.FailedToDeleteObject
            vfense_status_code = CustomerFailureCodes.UsersExistForCustomer

        elif default_in_list:
            msg = 'Can not delete the default customer'
            status_code = DbCodes.Unchanged
            generic_status_code = GenericFailureCodes.FailedToDeleteObject
            vfense_status_code = CustomerFailureCodes.CantDeleteDefaultCustomer

        else:
            msg = (
                'customer %s does not exist' %
                (' and '.join(customers_are_valid[2]))
            )
            status_code = DbCodes.Skipped
            generic_status_code = GenericCodes.InvalidId
            vfense_status_code = CustomerFailureCodes.InvalidCustomerName

        results = {
            ApiResultKeys.DB_STATUS_CODE: status_code,
            ApiResultKeys.DELETED_IDS: customers_deleted,
            ApiResultKeys.GENERIC_STATUS_CODE: generic_status_code,
            ApiResultKeys.VFENSE_STATUS_CODE: vfense_status_code,
            ApiResultKeys.MESSAGE: status + msg,
            ApiResultKeys.DATA: [],
            ApiResultKeys.USERNAME: user_name,
            ApiResultKeys.URI: uri,
            ApiResultKeys.HTTP_METHOD: method
        }

    except Exception as e:
        logger.exception(e)
        msg = 'Failed to remove customer %s: %s' % (customer_names, str(e))
        status_code = DbCodes.Errors
        generic_status_code = GenericFailureCodes.FailedToDeleteObject
        vfense_status_code = CustomerFailureCodes.FailedToRemoveCustomer

        results = {
            ApiResultKeys.DB_STATUS_CODE: status_code,
            ApiResultKeys.GENERIC_STATUS_CODE: generic_status_code,
            ApiResultKeys.VFENSE_STATUS_CODE: vfense_status_code,
            ApiResultKeys.DELETED_IDS: customers_deleted,
            ApiResultKeys.MESSAGE: status + msg,
            ApiResultKeys.DATA: [],
            ApiResultKeys.USERNAME: user_name,
            ApiResultKeys.URI: uri,
            ApiResultKeys.HTTP_METHOD: method
        }

    return(results)

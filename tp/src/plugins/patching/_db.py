import logging

from vFense.core._constants import *
from vFense.core.decorators import return_status_tuple, time_it
from vFense.plugins.patching import AppCollections, DownloadCollections, \
    FileCollections, AppsKey, AppsPerAgentKey, AppsIndexes, \
    AppsPerAgentIndexes, SupportedAppsKey, SupportedAppsPerAgentKey, \
    SupportedAppsPerAgentIndexes, CustomAppsKey, CustomAppsPerAgentKey, \
    CustomAppsPerAgentIndexes, AgentAppsKey, AgentAppsPerAgentKey, \
    AgentAppsPerAgentIndexes
from vFense.db.client import db_create_close, r

logging.config.fileConfig('/opt/TopPatch/conf/logging.config')
logger = logging.getLogger('rvapi')


@time_it
@db_create_close
@return_status_tuple
def update_apps_by_customer(
    customer_name, app_data, collection=AppCollections.AppsPerAgent,
    index_name=AppsPerAgentIndexes.CustomerName,
    conn=None):
    """ Update any keys for any apps collection by customer name
        This function should not be called directly.
    Args:
        customer_name (str): Name of the customer.
        app_data (dict): Dictionary of the key and values that you are updating.

    Kwargs:
        collection (str): The Application Collection that is going to be used.
        index_name (str): The name of the index that will be used during the search.

    Basic Usage:
        >>> from vFense.plugins.patching._db import update_app_per_agent_data_by_customer
        >>> customer_name = 'vFense'
        >>> app_data = {'customer_name': 'vFense'} 
        >>> collection = 'apps_per_agent'
        >>> index_name = 'customer_name'
        >>> update_app_per_agent_data_by_customer(customer_name,_app_data, collection, index_name)

    Return:
        Tuple (status_code, count, error, generated ids)
        >>> (2001, 1, None, [])
    """

    data = {}
    try:
        data = (
            r
            .table(collection)
            .get_all(
                customer_name, index=index_name
            )
            .update(app_data)
            .run(conn)
        )
    except Exception as e:
        logger.exception(e)

    return(data)


def update_os_apps_for_agent_by_customer(customer_name, app_data):
    """Update all apps for all agents by customer for 
        the apps_per_agent collection, using the customer_name
        index.
        This function should not be called directly.
    Args:
        customer_name (str): Name of the customer.
        app_data (dict): The data that you are updating.

    Basic Usage:
        >>> from vFense.plugins.patching._db import update_os_apps_for_agent_by_customer
        >>> customer_name = 'vFense'
        >>> app_data = {'customer_name': 'vFense'}
        >>> update_os_apps_for_agent_by_customer(customer_name, app_data)

    Return:
        Tuple (status_code, count, error, generated ids)
        >>> (2001, 1, None, [])
    """
    collection_name = AppCollections.AppsPerAgent
    index_name = AppsPerAgentIndexes.CustomerName
    return(
        update_apps_by_customer(
            customer_name, app_data,
            collection_name, index_name
        )
    )


def update_supported_apps_for_agent_by_customer(customer_name, app_data):
    """Update all apps for all agents by customer for 
        the supported_apps_per_agent collection, using the customer_name
        index.
        This function should not be called directly.
    Args:
        customer_name (str): Name of the customer.
        app_data (dict): The data that you are updating.

    Basic Usage:
        >>> from vFense.plugins.patching._db import update_supported_apps_for_agent_by_customer
        >>> customer_name = 'vFense'
        >>> app_data = {'customer_name': 'vFense'}
        >>> update_supported_apps_for_agent_by_customer(customer_name, app_data)

    Return:
        Tuple (status_code, count, error, generated ids)
        >>> (2001, 1, None, [])
    """
    collection_name = AppCollections.SupportedAppsPerAgent
    index_name = SupportedAppsPerAgentIndexes.CustomerName
    return(
        update_apps_by_customer(
            customer_name, app_data,
            collection_name, index_name
        )
    )


def update_custom_apps_for_agent_by_customer(customer_name, app_data):
    """Update all apps for all agents by customer for 
        the custom_apps_per_agent collection, using the customer_name
        index.
        This function should not be called directly.
    Args:
        customer_name (str): Name of the customer.
        app_data (dict): The data that you are updating.

    Basic Usage:
        >>> from vFense.plugins.patching._db import update_custom_apps_for_agent_by_customer
        >>> customer_name = 'vFense'
        >>> app_data = {'customer_name': 'vFense'}
        >>> update_custom_apps_for_agent_by_customer(customer_name, app_data)

    Return:
        Tuple (status_code, count, error, generated ids)
        >>> (2001, 1, None, [])
    """
    collection_name = AppCollections.CustomAppsPerAgent
    index_name = CustomAppsPerAgentIndexes.CustomerName
    return(
        update_apps_by_customer(
            customer_name, app_data,
            collection_name, index_name
        )
    )


def update_agent_apps_for_agent_by_customer(customer_name, app_data):
    """Update all apps for all agents by customer for 
        the agent_apps_per_agent collection, using the customer_name
        index.
        This function should not be called directly.
    Args:
        customer_name (str): Name of the customer.
        app_data (dict): The data that you are updating.

    Basic Usage:
        >>> from vFense.plugins.patching._db import update_agent_apps_for_agent_by_customer
        >>> customer_name = 'vFense'
        >>> app_data = {'customer_name': 'vFense'}
        >>> update_agent_apps_for_agent_by_customer(customer_name, app_data)

    Return:
        Tuple (status_code, count, error, generated ids)
        >>> (2001, 1, None, [])
    """
    collection_name = AppCollections.CustomAppsPerAgent
    index_name = CustomAppsPerAgentIndexes.CustomerName
    return(
        update_apps_by_customer(
            customer_name, app_data,
            collection_name, index_name
        )
    )


@time_it
@db_create_close
@return_status_tuple
def delete_apps_by_customer(
    customer_name, collection=AppCollections.AppsPerAgent,
    index_name=AppsPerAgentIndexes.CustomerName,
    conn=None):
    """Delete all apps for all agents by customer and app type
        This function should not be called directly.
    Args:
        customer_name (str): Name of the customer.

    Kwargs:
        collection (str): The Application Collection that is going to be used.
        index_name (str): The name of the index that will be used during the search.

    Basic Usage:
        >>> from vFense.plugins.patching._db import delete_apps_by_customer
        >>> customer_name = 'vFense'
        >>> collection = 'apps_per_agent'
        >>> index_name = 'customer_name'
        >>> delete_apps_by_customer(customer_name,_collection, index_name)

    Return:
        Tuple (status_code, count, error, generated ids)
        >>> (2001, 1, None, [])
    """

    data = {}
    try:
        data = (
            r
            .table(collection)
            .get_all(
                customer_name, index=index_name
            )
            .delete()
            .run(conn)
        )
    except Exception as e:
        logger.exception(e)

    return(data)


def delete_os_apps_for_agent_by_customer(customer_name):
    collection_name = AppCollections.AppsPerAgent
    index_name = AppsPerAgentIndexes.CustomerName
    """Delete all apps for all agents by customer for 
        the apps_per_agent collection, using the customer_name
        index.
        This function should not be called directly.
    Args:
        customer_name (str): Name of the customer.

    Basic Usage:
        >>> from vFense.plugins.patching._db import delete_os_apps_for_agent_by_customer
        >>> customer_name = 'vFense'
        >>> delete_os_apps_for_agent_by_customer(customer_name)

    Return:
        Tuple (status_code, count, error, generated ids)
        >>> (2001, 1, None, [])
    """
    return(
        delete_apps_by_customer(
            customer_name,
            collection_name,
            index_name
        )
    )


def delete_supported_apps_for_agent_by_customer(customer_name):
    collection_name = AppCollections.SupportedAppsPerAgent
    index_name = SupportedAppsPerAgentIndexes.CustomerName
    """Delete all apps for all agents by customer for 
        the supported_apps_per_agent collection, using the customer_name
        index.
        This function should not be called directly.
    Args:
        customer_name (str): Name of the customer.

    Basic Usage:
        >>> from vFense.plugins.patching._db import delete_supported_apps_for_agent_by_customer
        >>> customer_name = 'vFense'
        >>> delete_supported_apps_for_agent_by_customer(customer_name)

    Return:
        Tuple (status_code, count, error, generated ids)
        >>> (2001, 1, None, [])
    """
    return(
        delete_apps_by_customer(
            customer_name,
            collection_name,
            index_name
        )
    )


def delete_custom_apps_for_agent_by_customer(customer_name):
    collection_name = AppCollections.CustomAppsPerAgent
    index_name = CustomAppsPerAgentIndexes.CustomerName
    """Delete all apps for all agents by customer for 
        the custom_apps_per_agent collection, using the customer_name
        index.
        This function should not be called directly.
    Args:
        customer_name (str): Name of the customer.

    Basic Usage:
        >>> from vFense.plugins.patching._db import delete_custom_apps_for_agent_by_customer
        >>> customer_name = 'vFense'
        >>> delete_custom_apps_for_agent_by_customer(customer_name)

    Return:
        Tuple (status_code, count, error, generated ids)
        >>> (2001, 1, None, [])
    """
    return(
        delete_apps_by_customer(
            customer_name,
            collection_name,
            index_name
        )
    )


def delete_agent_apps_for_agent_by_customer(customer_name):
    collection_name = AppCollections.AgentAppsPerAgent
    index_name = AgentAppsPerAgentIndexes.CustomerName
    """Delete all apps for all agents by customer for 
        the agent_apps_per_agent collection, using the customer_name
        index.
        This function should not be called directly.
    Args:
        customer_name (str): Name of the customer.

    Basic Usage:
        >>> from vFense.plugins.patching._db import delete_agent_apps_for_agent_by_customer
        >>> customer_name = 'vFense'
        >>> delete_agent_apps_for_agent_by_customer(customer_name)

    Return:
        Tuple (status_code, count, error, generated ids)
        >>> (2001, 1, None, [])
    """
    return(
        delete_apps_by_customer(
            customer_name,
            collection_name,
            index_name
        )
    )

import logging
from datetime import datetime
from time import mktime

from vFense.core.agent import *
from vFense.core.agent._db import *
from vFense.core.customer.customers import get_customer, create_customer
from vFense.core.decorators import time_it, results_message

from vFense.db.client import r
from vFense.db.hardware import Hardware
from vFense.errorz.error_messages import AgentResults, GenericResults
from vFense.errorz.results import Results 
from vFense.errorz._constants import ApiResultKeys 
from vFense.errorz.status_codes import DbCodes, GenericCodes,\
    AgentCodes, AgentFailureCodes, GenericFailureCodes
from vFense.plugins.patching import *

logging.config.fileConfig('/opt/TopPatch/conf/logging.config')
logger = logging.getLogger('rvapi')


@time_it
def get_production_levels(customer_name):
    """
    Retrieve all the production levels that is in the database.
    :param customer_name: Name of the customer, where the agent is located.
    Basic Usage::
        >>> from vFense.core.agent.agents import get_production_levels
        >>> customer_name = 'default'
        >>> get_production_levels(customer_name)
        [
            u'Development',
            u'Production'
        ]
    """
    data = fetch_production_levels_from_agent(customer_name)
    return(data)


@time_it
def get_supported_os_codes():
    """
    Retrieve all the base operating systems codes that is in the database.
    Basic Usage::
        >>> from vFense.core.agent.agents import get_supported_os_codes
        >>> get_supported_os_codes()
        [
            u'windows',
            u'linux',
            u'darwin',
        ]
    """
    oses = ['windows', 'linux', 'darwin']
    return(oses)


@time_it
def get_supported_os_strings(customer_name):
    """
    Retrieve all the operating systems that is in the database.
    :param customer_name: Name of the customer, where the agent is located.
    Basic Usage::
        >>> from vFense.core.agent.agents import get_supported_os_strings
        >>> customer_name = 'default'
        >>> get_supported_os_strings(customer_name)
        [
            u'CentOS 6.5',
            u'Ubuntu 12.04',
            u'Windows 7 Professional Service Pack 1',
            u'Windows 8.1 '
        ]
    """
    data = fetch_supported_os_strings(customer_name)
    return(data)


@time_it
def get_all_agent_ids(customer_name=None, agent_os=None):
    """
    :param customer_name: (Optional) Name of the customer, where the agent
        is located
    :param agent_os: (Optional) linux or windows or darwin
    Basic Usage::
        >>> from vFense.core.agent.agents import get_all_agent_ids
        >>> customer_name = 'default'
        >>> agent_os = 'os_code'
        >>> get_all_agent_ids(customer_name, agent_os)
        [
            u'52faa1db-290a-47a7-a4cf-e4ad70e25c38',
            u'3ea8fd7a-8aad-40da-aff0-8da6fa5f8766'
        ]
    """

    if agent_os and customer_name:
        agents = fetch_agent_ids(customer_name, agent_os)

    elif agent_os and not customer_name:
        agents = fetch_agent_ids(agent_os=agent_os)

    elif not agent_os and customer_name:
        agents = fetch_agent_ids(customer_name)

    elif not agent_os and not customer_name:
        agents = fetch_agent_ids()

    return(agents)


@time_it
def get_agents_info(customer_name=None, agent_os=None, keys_to_pluck=None):
    """
    :param customer_name: (Optional) Name of the customer, where the agent
        is located
    :param agent_os: (Optional) The operating system you are filtering for.
        linux or windows or darwin
    :param keys_to_pluck: (Optional) Specific keys that you are retrieving
        from the database
    Basic Usage::
        >>> from vFense.core.agent.agents import get_agents_info
        >>> os_code = 'linux'
        >>> pluck = ['computer_name', 'agent_id']
        >>> get_agents_info(customer_name, os_code, keys_to_pluck=pluck)
        [
            {
                u'agent_id': u'52faa1db-290a-47a7-a4cf-e4ad70e25c38',
                u'computer_name': u'ubuntu'
            },
            {
                u'agent_id': u'3ea8fd7a-8aad-40da-aff0-8da6fa5f8766',
                u'computer_name': u'localhost.localdomain'
            }
        ]
    """

    if agent_os and not keys_to_pluck and customer_name:
        agents = (
            fetch_agents(
                customer_name=customer_name,
                filter_key=AgentKey.OsCode,
                filter_val=agent_os
            )
        )

    elif agent_os and not keys_to_pluck and not customer_name:
        agents = (
            fetch_agents(
                filter_key=AgentKey.OsCode,
                filter_val=agent_os
            )
        )

    elif agent_os and keys_to_pluck and customer_name:
        agents = (
            fetch_agents(
                customer_name=customer_name,
                filter_key=AgentKey.OsCode,
                filter_val=agent_os,
                keys_to_pluck=keys_to_pluck,
            )
        )

    elif agent_os and keys_to_pluck and not customer_name:
        agents = (
            fetch_agents(
                filter_key=AgentKey.OsCode,
                filter_val=agent_os,
                keys_to_pluck=keys_to_pluck,
            )
        )

    elif not agent_os and keys_to_pluck and customer_name:
        agents = (
            fetch_agents(
                customer_name=customer_name,
                keys_to_pluck=keys_to_pluck,
            )
        )

    elif not agent_os and keys_to_pluck and not customer_name:
        agents = (
            fetch_agents(
                keys_to_pluck=keys_to_pluck,
            )
        )

    elif not agent_os and not keys_to_pluck and not customer_name:
        agents = (
            fetch_agents()
        )

    elif not agent_os and not keys_to_pluck and customer_name:
        agents = (
            fetch_agents_collection(customer_name=customer_name)
        )

    return(agents)


@time_it
def get_agent_info(agent_id, keys_to_pluck=None):
    """
    :param agent_id: 36 character uuid of the agent you are updating
    :param keys_to_pluck: (Optional) Specific keys that you are retrieving
        from the database
    Basic Usage::
        >>> from vFense.core.agent.agents import get_agent_info
        >>> agent_id = '52faa1db-290a-47a7-a4cf-e4ad70e25c38'
        >>> keys_to_pluck = ['production_level', 'needs_reboot']
        >>> get_agent_info(agent_id, keys_to_pluck)
        {
            u'agent_id': u'52faa1db-290a-47a7-a4cf-e4ad70e25c38',
            u'production_level': u'Development'
        }
    """
    if not keys_to_pluck:
        agent_info = fetch_agent_info(agent_id)

    else:
        agent_info = fetch_agent_info(agent_id, keys_to_pluck)

    return(agent_info)


@time_it
@results_message
def update_agent_field(agent_id, field, value, username=None, uri=None, method=None):
    """
    :param agent_id: 36 character uuid of the agent you are updating
    :param field: The field you are going to update.
    :param value: The field will be updated to this value.

    Basic Usage::
        >>> from vFense.core.agent.agents import update_agent_field
        >>> agent_id = '0a1f9a3c-9200-42ef-ba63-f4fd17f0644c'
        >>> field = 'production_level'
        >>> value = 'Development'
        >>> update_agent_field(agent_id, field, value)
        {
            'uri': None,
            'rv_status_code': 1008,
            'http_method': None,
            'http_status': 200,
            'message': 'admin - agent 52faa1db-290a-47a7-a4cf-e4ad70e25c38 was updated',
            'data': {'needs_reboot': 'no'}
        }
    """
    try:
        data = {field: value}
        update_status = update_agent_data(agent_id, data)
        results = (
            update_status[0], agent_id, 'agent', data, update_status[2],
            username, uri, method
        )

    except Exception as e:
        results = (
            update_status[0], agent_id, 'agent', data, update_status[e],
            username, uri, method
        )
        logger.exception(results)

    return(results)


@time_it
@results_message
def update_agent_fields(agent_id, agent_data, username=None,
                        uri=None, method=None):
    """
    :param agent_id: 36 character uuid of the agent you are updating
    :param agent_data: Dictionary of the data that you are updating
    Basic Usage::
        >>> from vFense.core.agent.agents import update_agent_fields
        >>> agent_id = '0a1f9a3c-9200-42ef-ba63-f4fd17f0644c'
        >>> agent_data = {'production_level': 'Development'}
        >>> update_agent_fields(agent_id, agent_data)
        {
            'uri': None,
            'rv_status_code': 1008,
            'http_method': None,
            'http_status': 200,
            'message': 'admin - agent 52faa1db-290a-47a7-a4cf-e4ad70e25c38 was updated',
            'data': {'needs_reboot': 'no'}
        }
    """
    try:
        update_status = update_agent_data(agent_id, agent_data)
        results = (
            update_status[0], agent_id, 'agent', agent_data, update_status[2],
            username, uri, method
        )

    except Exception as e:
        results = (
            update_status[0], agent_id, 'agent', agent_data, update_status[e],
            username, uri, method
        )
        logger.exception(e)

    return(results)


@time_it
@results_message
def update_agent_status(agent_id, username=None, uri=None, method=None):
    """
    :param agent_id: 36 character uuid of the agent you are updating
    Basic Usage::
        >>> from vFense.core.agent.agents import update_agent_status
        >>> agent_id = '0a1f9a3c-9200-42ef-ba63-f4fd17f0644c'
        >>> update_agent_status(agent_id)
        {
            'uri': None,
            'rv_status_code': 1008,
            'http_method': None,
            'http_status': 200,
            'message': 'admin - agent 52faa1db-290a-47a7-a4cf-e4ad70e25c38 was updated',
            'data': {'needs_reboot': 'no'}
        }
    """
    status = update_agent_status.func_name + ' - '
    now = mktime(datetime.now().timetuple())
    agent_data = {
        AgentKey.LastAgentUpdate: r.epoch_time(now),
        AgentKey.AgentStatus: 'up'
    }
    status_code, count, error, generated_ids = (
        update_agent_data(agent_id, agent_data)
    )
    if status_code == DbCodes.Replaced:
        msg = 'agent_id %s updated'
        generic_status_code = GenericCodes.ObjectUpdated
        vfense_status_code = AgentCodes.AgentsUpdated

    elif status_code == DbCodes.Skipped:
        msg = 'agent_id %s does not exist'
        generic_status_code = GenericFailureCodes.FailedToUpdateObject
        vfense_status_code = AgentFailureCodes.AgentsDoesNotExist

    elif status_code == DbCodes.Errors:
        msg = 'agent_id %s could not be updated'
        generic_status_code = GenericFailureCodes.FailedToUpdateObject
        vfense_status_code = AgentFailureCodes.AgentsFailedToUpdate

    agent_data[AgentKey.LastAgentUpdate] = now

    results = {
        ApiResultKeys.DB_STATUS_CODE: status_code,
        ApiResultKeys.GENERIC_STATUS_CODE: generic_status_code,
        ApiResultKeys.VFENSE_STATUS_CODE: vfense_status_code,
        ApiResultKeys.MESSAGE: status + msg,
        ApiResultKeys.DATA: [],
        ApiResultKeys.USERNAME: username,
        ApiResultKeys.URI: uri,
        ApiResultKeys.HTTP_METHOD: method
    }

    return(results)


@time_it
def add_agent(system_info, hardware, username=None,
              customer_name=None, uri=None, method=None):
    """
    Add a new agent to the database
    :param system_info: Dictionary with system related info
    :param hardware:  List of dictionaries that rpresent the hardware
    """
    try:
        now = mktime(datetime.now().timetuple())
        agent_data = {}
        agent_data[AgentKey.AgentStatus] = 'up'
        agent_data[AgentKey.MachineType] = 'physical'
        agent_data[AgentKey.Tags] = []
        agent_data[AgentKey.NeedsReboot] = 'no'
        agent_data[AgentKey.DisplayName] = None
        agent_data[AgentKey.HostName] = None
        agent_data[AgentKey.CustomerName] = customer_name
        agent_data[AgentKey.Hardware] = hardware

        if not AgentKey.ProductionLevel in system_info:
            agent_data[AgentKey.ProductionLevel] = 'Production'

        if customer_name != 'default':
            cexists = get_customer(customer_name)
            if not cexists and len(customer_name) >= 1:
                create_customer(
                    customer_name, username=username,
                    uri=uri, method=method
                )

        for key, value in system_info.items():
            agent_data[key] = value

        agent_data[AgentKey.LastAgentUpdate] = r.epoch_time(now)

        object_status, object_count, error, generated_ids = (
            insert_agent_data(agent_data)
        )
        if object_status == DbCodes.Inserted and object_count > 0:
            agent_id = generated_ids[0]
            Hardware().add(agent_id, agent_data[AgentKey.Hardware])
            data = {
                AgentKey.AgentId: agent_id,
                AgentKey.CustomerName: agent_data[AgentKey.CustomerName],
                AgentKey.ComputerName: agent_data[AgentKey.ComputerName],
                AgentKey.Hardware: agent_data[AgentKey.Hardware],
                AgentKey.Tags: agent_data[AgentKey.Tags],
                AgentKey.OsCode: agent_data[AgentKey.OsCode],
                AgentKey.OsString: agent_data[AgentKey.OsString],
            }

            status = (
                AgentResults(
                    username, uri, method
                ).new_agent(agent_id, data)
            )

            logger.debug(status['message'])

        else:
            status = (
                GenericResults(
                    username, uri, method
                ).something_broke(agentid, 'agent', agent_added)
            )

            logger.info(status['message'])

    except Exception as e:
        status = (
            GenericResults(
                username, uri, method
            ).something_broke('new agent', 'agent', e)
        )

        logger.exception(status['message'])

    return(status)


@time_it
def update_agent(agent_id, system_info, hardware, rebooted,
                 username=None, customer_name=None,
                 uri=None, method=None):
    """Update various aspects of agent
    Args:
        agent_id (str): 36 character uuid of the agent you are updating
        system_info (dict): Dictionary with system related info
        hardware (dict):  List of dictionaries that rpresent the hardware
        rebooted (str): yes or no

    Kwargs:
        user_name (str): The name of the user who called this function.
        customer_name (str): The name of the customer.
        uri (str): The uri that was used to call this function.
        method (str): The HTTP methos that was used to call this function.
    """
    agent_data = {}

    try:
        now = mktime(datetime.now().timetuple())
        agent_orig_info = get_agent_info(agent_id)
        if agent_orig_info:
            agent_data[AgentKey.Hardware] = hardware

            for key, value in system_info.items():
                agent_data[key] = value

            agent_data[AgentKey.LastAgentUpdate] = (
                r.epoch_time(now)
            )
            agent_data[AgentKey.HostName] = (
                agent_orig_info.get(AgentKey.HostName, None)
            )
            agent_data[AgentKey.DisplayName] = (
                agent_orig_info.get(AgentKey.DisplayName, None)
            )

            if rebooted == 'yes':
                agent_data[AgentKey.NeedsReboot] = 'no'

            update_agent_data(agent_id, agent_data)
            Hardware().add(agent_id, hardware)
            status = (
                AgentResults(
                    username, uri, method
                ).startup(agent_id, agent_data)
            )
            logger.debug(status)


        else:
            status = (
                AgentResults(
                    username, uri, method
                ).startup_failed()
            )
            logger.warn(status)

    except Exception as e:
        status = (
            GenericResults(
                username, uri, method
            ).something_broke(agent_id, 'startup', e)
        )

        logger.exception(status)

    return(status)

@time_it
@results_message
def remove_all_agents_for_customer(
    customer_name, user_name=None,
    uri=None, method=None
    ):
    """Remove all agents from the system, filtered by customer_name
    Args:
        customer_name (str): The name of the customer.

    Kwargs:
        user_name (str): The name of the user who called this function.
        uri (str): The uri that was used to call this function.
        method (str): The HTTP methos that was used to call this function.

    Basic Usage:
        >>> from vFense.core.agent.agents import remove_all_agents_for_customer
        >>> customer_name = 'tester'
        >>> remove_all_agents_for_customer(customer_name)
    """
    status = remove_all_agents_for_customer.func_name + ' - '

    status_code, count, error, generated_ids = (
        delete_all_agents_for_customer(customer_name)
    )
    msg = 'total number of agents deleted: %s' % (str(count))
    if status_code == DbCodes.Deleted:
        generic_status_code = GenericCodes.ObjectDeleted
        vfense_status_code = AgentCodes.AgentsDeleted

    elif status_code == DbCodes.Skipped:
        generic_status_code = GenericCodes.DoesNotExists
        vfense_status_code = AgentFailureCodes.AgentsDoesNotExist

    elif status_code == DbCodes.DoesntExist:
        generic_status_code = GenericCodes.DoesNotExists
        vfense_status_code = AgentFailureCodes.AgentsDoesNotExist

    elif status_code == DbCodes.Errors:
        generic_status_code = GenericFailureCodes.FailedToDeleteObject
        vfense_status_code = AgentFailureCodes.AgentsFailedToDelete


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
def change_customer_for_agents(
    customer_name, user_name=None,
    uri=None, method=None
    ):
    """Move all agents from one customer to another 
    Args:
        customer_name (str): The name of the customer.

    Kwargs:
        user_name (str): The name of the user who called this function.
        uri (str): The uri that was used to call this function.
        method (str): The HTTP methos that was used to call this function.

    Basic Usage:
        >>> from vFense.core.agent.agents import change_customer_for_agents
        >>> customer_name = 'tester'
        >>> change_customer_for_agents(customer_name)
    """
    status = change_customer_for_agents.func_name + ' - '

    status_code, count, error, generated_ids = (
        move_all_agents_to_customer(customer_name)
    )
    msg = 'total number of agents moved: %s' % (str(count))
    if status_code == DbCodes.Replaced:
        generic_status_code = GenericCodes.ObjectUpdated
        vfense_status_code = AgentCodes.AgentsUpdated

    elif status_code == DbCodes.Skipped:
        generic_status_code = GenericCodes.DoesNotExists
        vfense_status_code = AgentFailureCodes.AgentsDoesNotExist

    elif status_code == DbCodes.DoesntExist:
        generic_status_code = GenericCodes.DoesNotExists
        vfense_status_code = AgentFailureCodes.AgentsDoesNotExist

    elif status_code == DbCodes.Errors:
        generic_status_code = GenericFailureCodes.FailedToUpdateObject
        vfense_status_code = AgentFailureCodes.AgentsFailedToUpdate

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

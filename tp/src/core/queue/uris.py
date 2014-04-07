import os
from vFense.core._constants import HTTPMethods
from vFense.core.queue._constants import *

def get_agent_results_uri(agent_id, operation):
    """Return back the http method and response uri for an operation.
    Args:
        agent_id (str): 36 character UUID
        operation (str): valid vFense operation.

    Basic Usage:
        >>> from vFense.receiver.agent_uris import get_agent_results_uri
        >>> agent_id = 'd4119b36-fe3c-4973-84c7-e8e3d72a3e02'
        >>> operation = 'install_os_apps'
        >>> get_agent_results_uri(agent_id, operation)

    Returns:
        Tuple
        ('put', '/rvl/v1/d4119b36-fe3c-4973-84c7-e8e3d72a3e02/core/results/reboot/?')

    """
    if operation == ValidOperations.INSTALL_OS_APPS:
        request_method = HTTPMethods.PUT
        response_uri = (
            os.path.join(
                BaseURIs.LISTENER, agent_id + ListenerURIs.INSTALL_OS_APPS
            )
        )

    elif operation == ValidOperations.INSTALL_CUSTOM_APPS:
        request_method = HTTPMethods.PUT
        response_uri = (
            os.path.join(
                BaseURIs.LISTENER, agent_id + ListenerURIs.INSTALL_CUSTOM_APPS
            )
        )

    elif operation == ValidOperations.INSTALL_SUPPORTED_APPS:
        request_method = HTTPMethods.PUT
        response_uri = (
            os.path.join(
                BaseURIs.LISTENER, agent_id + ListenerURIs.INSTALL_SUPPORTED_APPS
            )
        )

    elif operation == ValidOperations.INSTALL_AGENT_APPS:
        request_method = HTTPMethods.PUT
        response_uri = (
            os.path.join(
                BaseURIs.LISTENER, agent_id + ListenerURIs.INSTALL_AGENT_APPS
            )
        )

    elif operation == ValidOperations.UNINSTALL:
        request_method = HTTPMethods.PUT
        response_uri = (
            os.path.join(
                BaseURIs.LISTENER, agent_id + ListenerURIs.UNINSTALL
            )
        )

    elif operation == ValidOperations.UNINSTALL_AGENT:
        request_method = HTTPMethods.PUT
        response_uri = (
            os.path.join(
                BaseURIs.LISTENER, agent_id + ListenerURIs.UNINSTALL
            )
        )

    elif operation == ValidOperations.REBOOT:
        request_method = HTTPMethods.PUT
        response_uri = (
            os.path.join(
                BaseURIs.LISTENER, agent_id + ListenerURIs.REBOOT
            )
        )

    elif operation == ValidOperations.SHUTDOWN:
        request_method = HTTPMethods.PUT
        response_uri = (
            os.path.join(
                BaseURIs.LISTENER, agent_id + ListenerURIs.SHUTDOWN
            )
        )

    elif operation == ValidOperations.CHECKIN:
        request_method = HTTPMethods.GET
        response_uri = (
            os.path.join(
                BaseURIs.LISTENER, agent_id + ListenerURIs.CHECKIN
            )
        )

    elif operation == ValidOperations.STARTUP:
        request_method = HTTPMethods.PUT
        response_uri = (
            os.path.join(
                BaseURIs.LISTENER, agent_id + ListenerURIs.START_UP
            )
        )

    elif operation == ValidOperations.APPS_REFRESH:
        request_method = HTTPMethods.PUT
        response_uri = (
            os.path.join(
                BaseURIs.LISTENER, agent_id + ListenerURIs.APPS_REFRESH
            )
        )

    elif operation == ValidOperations.NEWAGENT:
        request_method = HTTPMethods.POST
        response_uri = (
            BaseURIs.LISTENER + ListenerURIs.NEWAGENT[1:]
        )

    elif operation == ValidOperations.RA:
        request_method = HTTPMethods.POST
        response_uri = (
            BaseURIs.LISTENER + ListenerURIs.RA[1:]
        )


    return(request_method, response_uri)

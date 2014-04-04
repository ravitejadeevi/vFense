import logging

from vFense.core._constants import *
from vFense.plugins.patching._constants import CommonAppKeys
from vFense.core.decorators import time_it, results_message
from vFense.plugins.patching._db import delete_os_apps_for_agent_by_customer, \
    delete_supported_apps_for_agent_by_customer, \
    delete_custom_apps_for_agent_by_customer, \
    delete_agent_apps_for_agent_by_customer

logging.config.fileConfig('/opt/TopPatch/conf/logging.config')
logger = logging.getLogger('rvapi')

@time_it
def remove_all_apps_for_customer(customer_name):
    delete_os_apps_for_agent_by_customer(customer_name)
    delete_supported_apps_for_agent_by_customer(customer_name)
    delete_custom_apps_for_agent_by_customer(customer_name)
    delete_agent_apps_for_agent_by_customer(customer_name)


@time_it
def update_all_apps_for_customer(customer_name):
    app_data = {CommonAppKeys.CustomerName: customer_name}
    update_os_apps_for_agent_by_customer(customer_name, app_data)
    update_supported_apps_for_agent_by_customer(customer_name, app_data)
    update_custom_apps_for_agent_by_customer(customer_name, app_data)
    update_agent_apps_for_agent_by_customer(customer_name, app_data)

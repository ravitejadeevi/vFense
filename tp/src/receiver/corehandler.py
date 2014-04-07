import logging

from vFense.operations.operation_manager import Operation
from vFense.operations import *
from vFense.core.queue.queue import AgentQueue

logging.config.fileConfig('/opt/TopPatch/conf/logging.config')
logger = logging.getLogger('rvapi')

#process that data!!


def process_queue_data(agent_id, username, customer_name, uri, method):
    agent_queue = AgentQueue(agent_id, customer_name).pop_agent_queue()
    for operation in agent_queue:
        if operation.get(OperationKey.OperationId):
            oper = (
                    Operation(username, customer_name, uri, method)
            )
            oper.update_operation_pickup_time(
                operation[OperationKey.OperationId], agent_id, CHECKIN
            )

    return agent_queue

import re
import logging
import logging.config
from time import mktime
from datetime import datetime

from vFense.plugins.patching import *
from vFense.operations import *
from vFense.operations.operation_manager import Operation
from vFense.plugins.patching.rv_db_calls import update_app_status
from vFense.core.queue._db import get_all_expired_jobs, delete_all_expired_jobs

logging.config.fileConfig('/opt/TopPatch/conf/logging.config')
logger = logging.getLogger('admin_scheduler')

def remove_expired_jobs_and_update_operations():
    epoch_time_now = mktime(datetime.now().timetuple())
    expired_jobs = get_all_expired_jobs(epoch_time_now)
    status_code, count, error, generated_ids = (
        delete_all_expired_jobs(epoch_time_now)
    )
    jobs_deleted = count
    msg = 'number of jobs expired: %s' % (str(jobs_deleted))
    logger.info(msg)
    for job in expired_jobs:
        operation = (
            Operation('admin', job[OperationKey.CustomerName], None, None)
        )

        operation.update_operation_expire_time(
            job[OperationKey.OperationId],
            job[OperationPerAgentKey.AgentId],
            job[OperationKey.Operation]
        )

        if job[OperationKey.Plugin] == RV_PLUGIN:

            if re.search('^install', job['operation']):
                app_status = {STATUS:  AVAILABLE}

            elif re.search('^uninstall', job['operation']):
                app_status = {STATUS:  INSTALLED}
            for app in job[AppsKey.FileData]:
                update_app_status(
                    job[OperationPerAgentKey.AgentId],
                    app[AppsKey.AppId],
                    job[OperationKey.Operation],
                    app_status
                )

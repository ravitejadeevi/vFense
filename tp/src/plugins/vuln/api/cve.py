from datetime import datetime
import tornado.httpserver
import tornado.web

import simplejson as json

from vFense.server.handlers import BaseHandler
import logging
import logging.config

from vFense.errorz.error_messages import GenericResults, PackageResults

from vFense.plugins.vuln.search.by_cve_id import RetrieveByCveId

from vFense.server.hierarchy.manager import get_current_customer_name
from vFense.server.hierarchy.decorators import authenticated_request

logging.config.fileConfig('/opt/TopPatch/conf/logging.config')
logger = logging.getLogger('rvapi')


class CveIdHandler(BaseHandler):
    @authenticated_request
    def get(self, cve_id):
        username = self.get_current_user().encode('utf-8')
        customer_name = get_current_customer_name(username)
        uri = self.request.uri
        method = self.request.method
        vuln = (
            RetrieveByCveId(
                username, customer_name, cve_id,
                uri, method
            )
        )
        results = vuln.get_cve()

        self.set_status(results['http_status'])
        self.set_header('Content-Type', 'application/json')
        self.write(json.dumps(results, indent=4))

 

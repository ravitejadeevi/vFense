import json
import logging
import logging.config

from vFense.core.api.base import BaseHandler
from vFense.core.decorators import convert_json_to_arguments
from vFense.core.decorators import authenticated_request

from vFense.core.permissions._constants import *
from vFense.core.permissions.permissions import verify_permission_for_user, \
    return_results_for_permissions

from vFense.core.permissions.decorators import check_permissions

from vFense.core.agent import *
from vFense.core.user import *

from vFense.core.user.users import get_user_property, \
    get_user_properties, get_properties_for_all_users, \
    create_user, remove_user, remove_users, change_password, \
    edit_user_properties, toggle_user_status

from vFense.core.customer.customers import add_user_to_customers, \
    remove_customers_from_user

from vFense.core.group.groups import add_user_to_groups, \
    remove_groups_from_user

from vFense.errorz._constants import *
from vFense.errorz.status_codes import GenericCodes
from vFense.errorz.error_messages import GenericResults

logging.config.fileConfig('/opt/TopPatch/conf/logging.config')
logger = logging.getLogger('rvapi')


class UserHandler(BaseHandler):

    @authenticated_request
    @check_permissions(Permissions.ADMINISTRATOR)
    def get(self, username):
        active_user = self.get_current_user()
        uri = self.request.uri
        method = self.request.method
        count = 0
        user_data = {}
        try:
            granted, status_code = (
                verify_permission_for_user(
                    active_user, Permissions.ADMINISTRATOR
                )
            )
            if not username or username == active_user:
                user_data = get_user_properties(active_user)
            elif username and granted:
                user_data = get_user_properties(username)
            elif username and not granted:
                results = (
                    return_results_for_permissions(
                        active_user, granted, status_code,
                        Permissions.ADMINISTRATOR, uri, method
                    )
                )

            if user_data:
                count = 1
                results = (
                    GenericResults(
                        active_user, uri, method
                    ).information_retrieved(user_data, count)
                ) 
            self.set_status(results['http_status'])
            self.set_header('Content-Type', 'application/json')
            self.write(json.dumps(results, indent=4))

        except Exception as e:
            results = (
                GenericResults(
                    active_user, uri, method
                ).something_broke(active_user, 'User', e)
            )
            logger.exception(e)
            self.set_status(results['http_status'])
            self.set_header('Content-Type', 'application/json')
            self.write(json.dumps(results, indent=4))


    @authenticated_request
    @convert_json_to_arguments
    @check_permissions(Permissions.ADMINISTRATOR)
    def post(self, username):
        active_user = self.get_current_user()
        active_customer = (
            get_user_property(username, UserKeys.CurrentCustomer)
        )
        uri = self.request.uri
        method = self.request.method
        results = None
        try:
            customer_context = (
                self.arguments.get('customer_context', active_customer)
            )
            action = self.arguments.get('action', 'add')

            ###Update Groups###
            group_ids = self.arguments.get('group_ids', None)
            if group_ids and isinstance(group_ids, list):
                if action == 'add':
                    print group_ids
                    results = (
                        add_user_to_groups(
                            username, customer_context, group_ids,
                            username, uri, method
                        )
                    )
                if action == 'delete':
                    print group_ids
                    results = (
                        remove_groups_from_user(
                            username, group_ids,
                            username, uri, method
                        )
                    )
            ###Update Customers###
            customer_names = self.arguments.get('customer_names')
            if customer_names and isinstance(customer_names, list):
                if action == 'add':
                    results = (
                        add_user_to_customers(
                            username, customer_names,
                            username, uri, method
                        )
                    )

                elif action == 'delete':
                    results = (
                        remove_customers_from_user(
                            username, customer_names,
                            username, uri, method
                        )
                    )

            if results:
                self.set_status(results['http_status'])
                self.set_header('Content-Type', 'application/json')
                self.write(json.dumps(results, indent=4))

            else:
                results = (
                    GenericResults(
                        active_user, uri, method
                    ).incorrect_arguments()
                )

                self.set_status(results['http_status'])
                self.set_header('Content-Type', 'application/json')
                self.write(json.dumps(results, indent=4))

        except Exception as e:
            results = (
                GenericResults(
                    active_user, uri, method
                ).something_broke(active_user, 'User', e)
            )
            logger.exception(e)
            self.set_status(results['http_status'])
            self.set_header('Content-Type', 'application/json')
            self.write(json.dumps(results, indent=4))


    @authenticated_request
    @convert_json_to_arguments
    @check_permissions(Permissions.ADMINISTRATOR)
    def put(self, username):
        active_user = self.get_current_user()
        uri = self.request.uri
        method = self.request.method
        results = None
        try:
            ###Password Changer###
            password = self.arguments.get('password', None)
            new_password = self.arguments.get('new_password', None)
            if password and new_password:
                results = (
                    change_password(
                        username, password, new_password,
                        username, uri, method
                    )
                )
            ###Update Personal Settings###
            data_dict = {
                ApiResultKeys.HTTP_METHOD: method,
                ApiResultKeys.URI: uri,
                ApiResultKeys.USERNAME: username
            }

            fullname = self.arguments.get('fullname', None)
            if fullname:
                data_dict[UserKeys.FullName] = fullname
                results = (
                    edit_user_properties(username, **data_dict)
                )

            email = self.arguments.get('email', None)
            if email:
                data_dict[UserKeys.Email] = email
                results = (
                    edit_user_properties(username, **data_dict)
                )

            ###Disable or Enable a User###
            enabled = self.arguments.get('enabled', None)
            if enabled:
                enabled.lower()
                if enabled == 'toggle':
                    results = (
                        toggle_user_status(username, username, uri, method)
                    )

            if results:
                self.set_status(results['http_status'])
                self.set_header('Content-Type', 'application/json')
                self.write(json.dumps(results, indent=4))

            else:
                results = (
                    GenericResults(
                        active_user, uri, method
                    ).incorrect_arguments()
                )

                self.set_status(results['http_status'])
                self.set_header('Content-Type', 'application/json')
                self.write(json.dumps(results, indent=4))

        except Exception as e:
            results = (
                GenericResults(
                    active_user, uri, method
                ).something_broke(active_user, 'User', e)
            )
            logger.exception(e)
            self.set_status(results['http_status'])
            self.set_header('Content-Type', 'application/json')
            self.write(json.dumps(results, indent=4))


    @authenticated_request
    @check_permissions(Permissions.ADMINISTRATOR)
    def delete(self, username):
        active_user = self.get_current_user()
        uri = self.request.uri
        method = self.request.method
        try:
            results = remove_user(
                username, active_user, uri, method
            )
            self.set_status(results['http_status'])
            self.set_header('Content-Type', 'application/json')
            self.write(json.dumps(results, indent=4))

        except Exception as e:
            results = (
                GenericResults(
                    active_user, uri, method
                ).something_broke(active_user, 'User', e)
            )
            logger.exception(e)
            self.set_status(results['http_status'])
            self.set_header('Content-Type', 'application/json')
            self.write(json.dumps(results, indent=4))


class UsersHandler(BaseHandler):

    @authenticated_request
    @check_permissions(Permissions.ADMINISTRATOR)
    def get(self):
        active_user = self.get_current_user()
        uri = self.request.uri
        method = self.request.method
        active_customer = (
            get_user_property(active_user, UserKeys.CurrentCustomer)
        )
        customer_context = self.get_argument('customer_context', None)
        all_customers = self.get_argument('all_customers', None)
        user_name = self.get_argument('user_name', None)
        count = 0
        user_data = {}
        try:
            granted, status_code = (
                verify_permission_for_user(
                    active_user, Permissions.ADMINISTRATOR
                )
            )
            if granted and not customer_context and not all_customers and not user_name:
                user_data = get_properties_for_all_users(active_customer)

            elif granted and customer_context and not all_customers and not user_name:
                user_data = get_properties_for_all_users(customer_name)

            elif granted and all_customers and not customer_context and not user_name:
                user_data = get_properties_for_all_users()

            elif granted and user_name and not customer_context and not all_customers:
                user_data = get_properties_for_user(user_name)
                if user_data:
                    user_data = [user_data]
                else:
                    user_data = []

            elif customer_context and not granted or all_customers and not granted:
                results = (
                    return_results_for_permissions(
                        active_user, granted, status_code,
                        Permissions.ADMINISTRATOR, uri, method
                    )
                )

            if user_data:
                count = len(user_data)
                results = (
                    GenericResults(
                        active_user, uri, method
                    ).information_retrieved(user_data, count)
                ) 
            self.set_status(results['http_status'])
            self.set_header('Content-Type', 'application/json')
            self.write(json.dumps(results, indent=4))

        except Exception as e:
            results = (
                GenericResults(
                    active_user, uri, method
                ).something_broke(active_user, 'User', e)
            )
            logger.exception(e)
            self.set_status(results['http_status'])
            self.set_header('Content-Type', 'application/json')
            self.write(json.dumps(results, indent=4))


    @authenticated_request
    @convert_json_to_arguments
    @check_permissions(Permissions.ADMINISTRATOR)
    def post(self):
        active_user = self.get_current_user()
        uri = self.request.uri
        method = self.request.method
        username = self.arguments.get('username')
        password = self.arguments.get('password')
        group_ids = self.arguments.get('group_ids')
        customer_names = self.arguments.get('customer_names', None)
        customer_context = self.arguments.get('customer_context')
        fullname = self.arguments.get('fullname', None)
        email = self.arguments.get('email', None)
        enabled = self.arguments.get('enabled', 'no')
        try:
            if not isinstance(group_ids, list):
                group_ids = group_ids.split()

            if customer_names:
                if not isinstance(customer_names, list):
                    customer_names = customer_names.split(',')

            results = create_user(
                username, fullname, password,
                group_ids, customer_context, email,
                enabled, active_user, uri, method
            )
            if results['rv_status_code'] == GenericCodes.ObjectCreated:
                if customer_names:
                    add_user_to_customers(
                        username, customer_names,
                        active_user, uri, method
                    )
            self.set_status(results['http_status'])
            self.set_header('Content-Type', 'application/json')
            self.write(json.dumps(results, indent=4))

        except Exception as e:
            results = (
                GenericResults(
                    active_user, uri, method
                ).something_broke(active_user, 'User', e)
            )
            logger.exception(e)
            self.set_status(results['http_status'])
            self.set_header('Content-Type', 'application/json')
            self.write(json.dumps(results, indent=4))


    @authenticated_request
    @convert_json_to_arguments
    @check_permissions(Permissions.ADMINISTRATOR)
    def delete(self):
        active_user = self.get_current_user()
        uri = self.request.uri
        method = self.request.method
        usernames = self.arguments.get('usernames')
        try:
            if not isinstance(usernames, list):
                usernames = usernames.split()

            results = remove_users(
                usernames, active_user, uri, method
            )
            self.set_status(results['http_status'])
            self.set_header('Content-Type', 'application/json')
            self.write(json.dumps(results, indent=4))

        except Exception as e:
            results = (
                GenericResults(
                    active_user, uri, method
                ).something_broke(active_user, 'User', e)
            )
            logger.exception(e)
            self.set_status(results['http_status'])
            self.set_header('Content-Type', 'application/json')
            self.write(json.dumps(results, indent=4))



import logging                                                                                                     

from vFense.core._constants import *
from vFense.errorz._constants import *
from vFense.core.user import *
from vFense.core.user._constants import *
from vFense.core.group import *
from vFense.core.group._constants import *
from vFense.core.user._db import insert_user, fetch_user, fetch_users, \
    delete_user, update_user, fetch_user_and_all_properties, \
    fetch_users_and_all_properties
from vFense.core.group.groups import validate_group_ids, \
    add_user_to_groups, remove_groups_from_user
from vFense.core.customer.customers import get_customer, \
    add_user_to_customers, remove_customers_from_user
from vFense.utils.security import Crypto, check_password
from vFense.core.decorators import results_message, time_it
from vFense.errorz.status_codes import *

logging.config.fileConfig('/opt/TopPatch/conf/logging.config')
logger = logging.getLogger('rvapi')


@time_it
def get_user(username, without_fields=['password']):
    """Retrieve a user from the database
    Args:
        username (str): Name of the user.

    Kwargs:
        without_fields (list): List of fields you do not want to include.

    Basic Usage:
        >>> from vFense.user.users import get_user
        >>> username = 'admin'
        >>> get_user(username, without_fields=['password'])

    Return:
        Dictionary of user properties.
        {
            u'current_customer': u'default',
            u'enabled': True,
            u'full_name': u'TopPatchAgentCommunicationAccount',
            u'default_customer': u'default',
            u'user_name': u'agent',
            u'email': u'admin@toppatch.com'
        }
    """
    data = fetch_user(username, without_fields)
    return(data)


@time_it
def get_user_property(username, user_property):
    """Retrieve user property.
    Args:
        username (str):  Name of the user.
        user_property (str): Property you want to retrieve.

    Basic Usage:
        >>> from vFense.user.users get_user_property
        >>> username = 'admin'
        >>> user_property = 'current_customer'
        >>> get_user_property(username, user_property)

    Return:
        String
    """
    user_data = fetch_user(username)
    user_key = None
    if user_data:
        user_key = user_data.get(user_property)

    return(user_key)

@time_it
def get_user_properties(username):
    """Retrieve a user and all of its properties by username.
    Args:
        username (str): Name of the user.

    Basic Usage:
        >>> from vFense.user.user import get_user_and_all_properties
        >>> username = 'admin'
        >>> get_user_and_all_properties(username')

    Return:
        Dictionary of user properties.
        {
            "current_customer": "default", 
            "customers": [
                {
                    "admin": true, 
                    "name": "default"
                }
            ], 
            "groups": [
                {
                    "group_id": "1b74a706-34e5-482a-bedc-ffbcd688f066", 
                    "group_name": "Administrator"
                }
            ], 
                "default_customer": "default", 
                "user_name": "admin", 
                "permissions": [
                    "administrator"
                ]
        }
    """
    user_data = fetch_user_and_all_properties(username)
    return(user_data)


@time_it
def get_properties_for_all_users(customer_name=None):
    """Retrieve users and all of its properties by customer_name.
    Kwargs:
        customer_name (str): Name of the customer.

    Basic Usage:
        >>> from vFense.user.user import get_properties_for_all_users
        >>> customer_name = 'default'
        >>> get_properties_for_all_users(customer_name')

    Return:
        List of users and their properties.
        [
            {
                "current_customer": "default", 
                "customers": [
                    {
                        "admin": true, 
                        "name": "default"
                    }
                ], 
                "groups": [
                    {
                        "group_id": "1b74a706-34e5-482a-bedc-ffbcd688f066", 
                        "group_name": "Administrator"
                    }
                ], 
                    "default_customer": "default", 
                    "user_name": "admin", 
                    "permissions": [
                        "administrator"
                    ]
            }
        ]
    """
    user_data = fetch_users_and_all_properties(customer_name)
    return(user_data)


@time_it
def get_users(customer_name=None, username=None, without_fields=None):
    """Retrieve all users that is in the database by customer_name or
        all of the customers or by regex.

    Kwargs:
        customer_name (str): Name of the customer, where the agent
            is located.
        username (str): Name of the user you are searching for.
            This is a regular expression match.
        without_fields (list): List of fields you do not want to include.

    Basic Usage::
        >>> from vFense.user.users import get_users
        >>> customer_name = 'default'
        >>> username = 'al'
        >>> without_fields = ['password']
        >>> get_users(customer_name, username, without_fields)

    Returns:
        List of users:
        [
            {
                "current_customer": "default", 
                "email": "test@test.org", 
                "full_name": "is doing it", 
                "default_customer": "default", 
                "user_name": "alien", 
                "id": "ba9682ef-7adf-4916-8002-9637485b30d8", 
                "customer_name": "default"
            }
        ]
    """
    data = fetch_users(customer_name, username, without_fields) 
    return(data)


@time_it
@results_message
def create_user(
    username, fullname, password, group_ids,
    customer_name, email, enabled='no', user_name=None,
    uri=None, method=None
    ):
    """Add a new user into vFense
    Args:
        username (str): The name of the user you are creating.
        fullname (str): The full name of the user you are creating.
        password (str): The unencrypted password of the user.
        group_ids (list): List of vFense group ids to add the user too.
        customer_name (str): The customer, this user will be part of.
        email (str): Email address of the user.
        enabled (str): yes or no
            Default=no

    Kwargs:
        user_name (str): The name of the user who called this function.
        uri (str): The uri that was used to call this function.
        method (str): The HTTP methos that was used to call this function.

    Basic Usage:
        >>> from vFense.user.users import create_user
        >>> username = 'testing123'
        >>> fullname = 'testing 4 life'
        >>> password = 'Testing123#'
        >>> group_ids = ['8757b79c-7321-4446-8882-65457f28c78b']
        >>> customer_name = 'default'
        >>> email = 'test@test.org'
        >>> enabled = 'yes'
        >>> create_user(
                username, fullname, password,
                group_ids, customer_name, email, enabled
            )

    Return:
        Dictionary of the status of the operation.
        {
            'uri': None,
            'rv_status_code': 1010,
            'http_method': None,
            'http_status': 200,
            'message': 'None - create user testing123 was created',
            'data': {
                'current_customer': 'default',
                'full_name': 'tester4life',
                'default_customer': 'default',
                'password': '$2a$12$HFAEabWwq8Hz0TIZ.jV59eHLoy0DdogdtR9TgvZnBCye894oljZOe',
                'user_name': 'testing123',
                'enabled': 'yes',
                'email': 'test@test.org'
            }
        }
    """

    user_exist = get_user(username)
    pass_strength = check_password(password)
    status = create_user.func_name + ' - '
    generated_ids = []
    generic_status_code = 0
    vfense_status_code = 0
    if enabled != CommonKeys.YES or enabled != CommonKeys.NO:
        enabled = CommonKeys.NO
    try:
        if not user_exist and pass_strength[0]:
            encrypted_password = Crypto().hash_bcrypt(password)
            customer_is_valid = get_customer(customer_name)
            groups_are_valid = validate_group_ids(group_ids, customer_name)

            if customer_is_valid and groups_are_valid[0]:
                user_data = (
                    {
                        UserKeys.CurrentCustomer: customer_name,
                        UserKeys.DefaultCustomer: customer_name,
                        UserKeys.FullName: fullname,
                        UserKeys.Password: encrypted_password,
                        UserKeys.UserName: username,
                        UserKeys.Enabled: enabled,
                        UserKeys.Email: email
                    }
                )
                object_status, object_count, error, generated_ids = (
                    insert_user(user_data)
                )

                add_user_to_customers(
                    username, [customer_name],
                    user_name, uri, method
                )

                add_user_to_groups(
                    username, customer_name, group_ids,
                    user_name, uri, method
                )
                if object_status == DbCodes.Inserted:
                    msg = 'user name %s created' % (username)
                    generic_status_code = GenericCodes.ObjectCreated
                    vfense_status_code = UserCodes.UserCreated

            elif not customer_is_valid and groups_are_valid[0]:
                msg = 'customer name %s does not exist' % (customer_name)
                object_status = GenericFailureCodes.FailedToCreateObject
                generic_status_code = GenericCodes.InvalidId
                vfense_status_code = CustomerFailureCodes.CustomerDoesNotExists

            elif not groups_are_valid[0] and customer_is_valid:
                msg = 'group ids %s does not exist' % (groups_are_valid[2])
                object_status = GenericCodes.FailedToCreateObject
                generic_status_code = GenericCodes.InvalidId
                vfense_status_code = GroupFailureCodes.InvalidGroupId

            else:
                group_error = (
                    'group ids %s does not exist' % (groups_are_valid[2])
                )
                customer_error = (
                    'customer name %s does not exist' % (customer_name)
                )
                msg = group_error + ' and ' + customer_error
                object_status = GenericFailureCodes.FailedToCreateObject
                generic_status_code = GenericFailureCodes.FailedToCreateObject
                vfense_status_code = UserFailureCodes.UserNameExists

        elif user_exist:
            msg = 'username %s already exists' % (username)
            object_status = GenericCodes.ObjectExists
            generic_status_code = GenericCodes.ObjectExists
            vfense_status_code = UserFailureCodes.UserNameExists

        elif not pass_strength[0]:
            msg = (
                    'password does not meet the min requirements: strength=%s'
                    % (pass_strength[1])
            )
            object_status = GenericFailureCodes.FailedToCreateObject
            generic_status_code = GenericFailureCodes.FailedToCreateObject
            vfense_status_code = UserFailureCodes.WeakPassword

        results = {
            ApiResultKeys.DB_STATUS_CODE: object_status,
            ApiResultKeys.GENERIC_STATUS_CODE: generic_status_code,
            ApiResultKeys.VFENSE_STATUS_CODE: vfense_status_code,
            ApiResultKeys.MESSAGE: status + msg,
            ApiResultKeys.GENERATED_IDS: generated_ids,
            ApiResultKeys.DATA: [],
            ApiResultKeys.USERNAME: user_name,
            ApiResultKeys.URI: uri,
            ApiResultKeys.HTTP_METHOD: method
        }

    except Exception as e:
        logger.exception(e)
        msg = 'Failed to create user %s: %s' % (username, str(e))
        status_code = DbCodes.Errors
        generic_status_code = GenericFailureCodes.FailedToCreateObject
        vfense_status_code = UserFailureCodes.FailedToCreateUser

        results = {
            ApiResultKeys.DB_STATUS_CODE: status_code,
            ApiResultKeys.GENERIC_STATUS_CODE: generic_status_code,
            ApiResultKeys.VFENSE_STATUS_CODE: vfense_status_code,
            ApiResultKeys.MESSAGE: status + msg,
            ApiResultKeys.GENERATED_IDS: [],
            ApiResultKeys.DATA: [],
            ApiResultKeys.USERNAME: user_name,
            ApiResultKeys.URI: uri,
            ApiResultKeys.HTTP_METHOD: method
        }

    return(results)


@time_it
@results_message
def remove_user(username, user_name=None, uri=None, method=None):
    """Remove a user from vFense
    Args:
        username (str): The name of the user you are deleteing.

    Kwargs:
        user_name (str): The name of the user who called this function.
        uri (str): The uri that was used to call this function.
        method (str): The HTTP methos that was used to call this function.

    Return:
        Dictionary of the status of the operation.
    """

    user_exist = get_user(username)
    status = remove_user.func_name + ' - '
    usernames_not_to_delete = []
    usernames_to_delete = []
    try:
        if user_exist and username != DefaultUser.ADMIN:
            remove_groups_from_user(username)
            remove_customers_from_user(username)
            usernames_to_delete.append(username)

            object_status, object_count, error, generated_ids = (
                delete_user(username)
            )

            if object_status == DbCodes.Inserted:
                generic_status_code = GenericCodes.ObjectDeleted
                vfense_status_code = UserCodes.UserDeleted
                msg = 'User removed %s' % (username)

        elif username == DefaultUser.ADMIN:
            msg = 'Can not delete the %s user' % (username)
            usernames_not_to_delete.append(username)
            object_status = DbCodes.Skipped
            generic_status_code = GenericCodes.CouldNotBeDeleted
            vfense_status_code = UserFailureCodes.AdminUserCanNotBeDeleted

        else:
            msg = 'User does not exist %s' % (username)
            usernames_not_to_delete.append(username)
            object_status = DbCodes.Skipped
            generic_status_code = GenericCodes.InvalidId
            vfense_status_code = UserFailureCodes.UserNameDoesNotExists

        results = {
            ApiResultKeys.DB_STATUS_CODE: object_status,
            ApiResultKeys.GENERIC_STATUS_CODE: generic_status_code,
            ApiResultKeys.VFENSE_STATUS_CODE: vfense_status_code,
            ApiResultKeys.MESSAGE: status + msg,
            ApiResultKeys.UNCHANGED_IDS: usernames_not_to_delete,
            ApiResultKeys.DELETED_IDS: usernames_to_delete,
            ApiResultKeys.DATA: [],
            ApiResultKeys.USERNAME: user_name,
            ApiResultKeys.URI: uri,
            ApiResultKeys.HTTP_METHOD: method
        }


    except Exception as e:
        logger.exception(e)
        msg = 'Failed to remove user %s: %s' % (username, str(e))
        status_code = DbCodes.Errors
        generic_status_code = GenericFailureCodes.FailedToDeleteObject
        vfense_status_code = UserFailureCodes.FailedToRemoveUser

        results = {
            ApiResultKeys.DB_STATUS_CODE: status_code,
            ApiResultKeys.GENERIC_STATUS_CODE: generic_status_code,
            ApiResultKeys.VFENSE_STATUS_CODE: vfense_status_code,
            ApiResultKeys.MESSAGE: status + msg,
            ApiResultKeys.UNCHANGED_IDS: usernames_not_to_delete,
            ApiResultKeys.DELETED_IDS: usernames_to_delete,
            ApiResultKeys.DATA: [],
            ApiResultKeys.USERNAME: user_name,
            ApiResultKeys.URI: uri,
            ApiResultKeys.HTTP_METHOD: method
        }

    return(results)


@time_it
@results_message
def remove_users(usernames, user_name=None, uri=None, method=None):
    """Remove a user from vFense
    Args:
        usernames (list): List of usernames that will be deleted.

    Kwargs:
        user_name (str): The name of the user who called this function.
        uri (str): The uri that was used to call this function.
        method (str): The HTTP methos that was used to call this function.

    Return:
        Dictionary of the status of the operation.
    """

    status = change_password.func_name + ' - '
    usernames_not_to_delete = []
    usernames_to_delete = []
    generic_status_code = 0
    vfense_status_code = 0
    try:
        if not isinstance(usernames, list):
            usernames = usernames.split(',')
        for username in usernames:
            user_exist = get_user(username)
            status = remove_users.func_name + ' - '
            if user_exist and username != DefaultUser.ADMIN:
                remove_groups_from_user(username)
                remove_customers_from_user(username)
                usernames_to_delete.append(username)

            elif username == DefaultUser.ADMIN:
                msg = 'Can not delete the %s user' % (username)
                usernames_not_to_delete.append(username)
                generic_status_code = GenericCodes.CouldNotBeDeleted
                vfense_status_code = UserFailureCodes.AdminUserCanNotBeDeleted

            else:
                msg = 'User does not exist %s' % (username)
                usernames_not_to_delete.append(username)
                generic_status_code = GenericCodes.InvalidId
                vfense_status_code = UserFailureCodes.UserNameDoesNotExists

        if len(usernames_to_delete) > 0:
            object_status, object_count, error, generated_ids = (
                delete_users(usernames_to_delete)
            )

            if object_status == DbCodes.Inserted:
                generic_status_code = GenericCodes.ObjectDeleted
                vfense_status_code = UserCodes.UserDeleted
                msg = 'Users removed %s' % (' and '.join(usernames_to_delete))

        else:
            object_status = DbCodes.Unchanged
            generic_status_code = GenericFailureCodes.FailedToDeleteObject
            vfense_status_code = UserFailureCodes.FailedToRemoveUser
            msg = 'Users can not be removed %s' % (
                ' and '.join(usernames_not_to_delete))

        results = {
            ApiResultKeys.DB_STATUS_CODE: object_status,
            ApiResultKeys.GENERIC_STATUS_CODE: generic_status_code,
            ApiResultKeys.VFENSE_STATUS_CODE: vfense_status_code,
            ApiResultKeys.MESSAGE: status + msg,
            ApiResultKeys.UNCHANGED_IDS: usernames_not_to_delete,
            ApiResultKeys.DELETED_IDS: usernames_to_delete,
            ApiResultKeys.DATA: [],
            ApiResultKeys.USERNAME: user_name,
            ApiResultKeys.URI: uri,
            ApiResultKeys.HTTP_METHOD: method
        }


    except Exception as e:
        logger.exception(e)
        msg = 'Failed to remove user %s: %s' % (username, str(e))
        generic_status_code = GenericFailureCodes.FailedToDeleteObject
        vfense_status_code = UserFailureCodes.FailedToRemoveUser

        results = {
            ApiResultKeys.DB_STATUS_CODE: DbCodes.Errors,
            ApiResultKeys.GENERIC_STATUS_CODE: generic_status_code,
            ApiResultKeys.VFENSE_STATUS_CODE: vfense_status_code,
            ApiResultKeys.MESSAGE: status + msg,
            ApiResultKeys.UNCHANGED_IDS: usernames_not_to_delete,
            ApiResultKeys.DELETED_IDS: usernames_to_delete,
            ApiResultKeys.DATA: [],
            ApiResultKeys.USERNAME: user_name,
            ApiResultKeys.URI: uri,
            ApiResultKeys.HTTP_METHOD: method
        }

    return(results)



@time_it
@results_message
def change_password(
    username, password, new_password,
    user_name=None, uri=None, method=None
    ):
    """Change password for a user.
    Args:
        username (str): The name of the user you are deleteing.
        password (str): Original password.
        new_password (str): New password.

    Kwargs:
        user_name (str): The name of the user who called this function.
        uri (str): The uri that was used to call this function.
        method (str): The HTTP methos that was used to call this function.

    Return:
        Dictionary of the status of the operation.
        {
            'uri': None,
            'rv_status_code': 1008,
            'http_method': None,
            'http_status': 200,
            'message': 'None - change_password - Password changed for user admin - admin was updated',
            'data': []
        }
    """
    user_exist = get_user(username, without_fields=None)
    status = change_password.func_name + ' - '
    try:
        generic_status_code = 0
        vfense_status_code = 0
        if user_exist:
            pass_strength = check_password(new_password)
            original_encrypted_password = user_exist[UserKeys.Password].encode('utf-8')
            original_password_verified = (
                Crypto().verify_bcrypt_hash(password, original_encrypted_password)
            )
            encrypted_new_password = Crypto().hash_bcrypt(new_password)
            new_password_verified_against_orignal_password = (
                Crypto().verify_bcrypt_hash(new_password, original_encrypted_password)
            )
            if (original_password_verified and pass_strength[0] and
                    not new_password_verified_against_orignal_password):

                user_data = {UserKeys.Password: encrypted_new_password}

                object_status, object_count, error, generated_ids = (
                    update_user(username, user_data)
                )

                if object_status == DbCodes.Replaced:
                    msg = 'Password changed for user %s - ' % (username)
                    generic_status_code = GenericCodes.ObjectUpdated
                    vfense_status_code = UserCodes.PasswordChanged

            elif new_password_verified_against_orignal_password:
                msg = 'New password is the same as the original - user %s - ' % (username)
                object_status = DbCodes.Unchanged
                generic_status_code = GenericFailureCodes.FailedToUpdateObject
                vfense_status_code = UserFailureCodes.NewPasswordSameAsOld

            elif original_password_verified and not pass_strength[0]:
                msg = 'New password is to weak for user %s - ' % (username)
                object_status = DbCodes.Unchanged
                generic_status_code = GenericFailureCodes.FailedToUpdateObject
                vfense_status_code = UserFailureCodes.WeakPassword

            elif not original_password_verified:
                msg = 'Password not verified for user %s - ' % (username)
                object_status = DbCodes.Unchanged
                generic_status_code = GenericFailureCodes.FailedToUpdateObject
                vfense_status_code = UserFailureCodes.InvalidPassword

            results = {
                ApiResultKeys.DB_STATUS_CODE: object_status,
                ApiResultKeys.GENERIC_STATUS_CODE: generic_status_code,
                ApiResultKeys.VFENSE_STATUS_CODE: vfense_status_code,
                ApiResultKeys.MESSAGE: status + msg,
                ApiResultKeys.DATA: [],
                ApiResultKeys.USERNAME: user_name,
                ApiResultKeys.URI: uri,
                ApiResultKeys.HTTP_METHOD: method
            }


        else:
            msg = 'User %s does not exist - ' % (username)
            object_status = DbCodes.Skipped
            generic_status_code = GenericCodes.InvalidId
            vfense_status_code = UserFailureCodes.UserNameDoesNotExists

            results = {
                ApiResultKeys.DB_STATUS_CODE: object_status,
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
        status_code = DbCodes.Errors
        generic_status_code = GenericFailureCodes.FailedToUpdateObject
        vfense_status_code = UserFailureCodes.FailedToUpdateUser
        msg = 'Failed to update password for user %s: %s' % (username, str(e))

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
def edit_user_properties(username, **kwargs):
    """ Edit the properties of a customer. 
    Args:
        username (str): Name of the user you are editing.

    Kwargs:
        full_name (str): The full name of the user
        email (str): The email address of the user
        user_name (str): The name of the user who called this function.
        uri (str): The uri that was used to call this function.
        method (str): The HTTP methos that was used to call this function.

    Return:
        Dictionary of the status of the operation.
        {
            'uri': None,
            'rv_status_code': 1008,
            'http_method': None,
            'http_status': 200,
            'message': 'None - edit_user_properties - admin was updated',
            'data': {
                'full_name': 'vFense Admin'
            }
        }
    """

    if not kwargs.get('user_name'):
        user_name = None
    else:
        user_name = kwargs.pop('user_name')

    if not kwargs.get('uri'):
        uri = None
    else:
        uri = kwargs.pop('uri')

    if not kwargs.get('method'):
        method = None
    else:
        method = kwargs.pop('method')

    if kwargs.get(UserKeys.Password):
        kwargs.pop(UserKeys.Password)

    user_exist = get_user(username, without_fields=None)
    status = edit_user_properties.func_name + ' - '
    generic_status_code = 0
    vfense_status_code = 0
    try:
        if user_exist:
            object_status, object_count, error, generated_ids = (
                update_user(username, kwargs)
            )
            if object_status == DbCodes.Replaced:
                generic_status_code = GenericCodes.ObjectUpdated
                vfense_status_code = UserCodes.UserUpdated

            elif object_status == DbCodes.Unchanged:
                generic_status_code = GenericCodes.ObjectUnchanged
                vfense_status_code = UserCodes.UserUnchanged

        else:
            object_status = DbCodes.Skipped
            generic_status_code = GenericCodes.InvalidId
            vfense_status_code = UserFailureCodes.UserNameDoesNotExists
            error = 'User %s does not exist - ' % (username)

        results = {
            ApiResultKeys.DB_STATUS_CODE: object_status,
            ApiResultKeys.GENERIC_STATUS_CODE: generic_status_code,
            ApiResultKeys.VFENSE_STATUS_CODE: vfense_status_code,
            ApiResultKeys.MESSAGE: status + str(error),
            ApiResultKeys.DATA: [kwargs],
            ApiResultKeys.USERNAME: user_name,
            ApiResultKeys.URI: uri,
            ApiResultKeys.HTTP_METHOD: method
        }

    except Exception as e:
        logger.exception(e)
        generic_status_code = GenericFailureCodes.FailedToUpdateObject
        vfense_status_code = UserFailureCodes.FailedToUpdateUser
        msg = 'Failed to update properties for user %s: %s' % (username, str(e))

        results = {
            ApiResultKeys.DB_STATUS_CODE: DbCodes.Errors,
            ApiResultKeys.GENERIC_STATUS_CODE: generic_status_code,
            ApiResultKeys.VFENSE_STATUS_CODE: vfense_status_code,
            ApiResultKeys.USERNAME: username,
            ApiResultKeys.MESSAGE: status + msg,
            ApiResultKeys.DATA: [kwargs],
            ApiResultKeys.USERNAME: user_name,
            ApiResultKeys.URI: uri,
            ApiResultKeys.HTTP_METHOD: method
        }

    return(results)

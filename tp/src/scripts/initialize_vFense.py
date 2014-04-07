import os
import sys
import re
import pwd
import argparse
import shutil
import signal
import subprocess
from time import sleep
import logging, logging.config

import create_indexes as ci
import nginx_config_creator as ncc
from vFense import *
from vFense.supported_platforms import *
from vFense.utils.security import generate_pass, check_password
from vFense.utils.common import pick_valid_ip_address
from vFense.db.client import db_connect, r


from vFense.core.user._constants import *
from vFense.core.group._constants import *
from vFense.core.customer._constants import *
from vFense.core.permissions._constants import *
import vFense.core.group.groups as group
import vFense.core.customer.customers as customer
import vFense.core.user.users as user

from vFense.plugins import monit
from vFense.plugins.vuln.cve.parser import load_up_all_xml_into_db
from vFense.plugins.vuln.windows.parser import parse_bulletin_and_updatedb
from vFense.plugins.vuln.ubuntu.parser import begin_usn_home_page_processing

logging.config.fileConfig('/opt/TopPatch/conf/logging.config')
logger = logging.getLogger('rvapi')


if os.getuid() != 0:
    print 'MUST BE ROOT IN ORDER TO RUN'
    sys.exit(1)

parser = argparse.ArgumentParser(description='Initialize vFense Options')
parser.add_argument(
    '--dnsname', dest='dns_name', default=None,
    help='Pass the DNS Name of the patching Server'
)
parser.add_argument(
    '--ipaddress', dest='ip_address', default=pick_valid_ip_address(),
    help='Pass the IP Address of the patching Server'
)
parser.add_argument(
    '--password', dest='admin_password', default=generate_pass(),
    help='Pass the password to use for the admin User. Default is a random generated password'
)
parser.add_argument(
    '--listener_count', dest='listener_count', default=10,
    help='The number of vFense_listener daemons to run at once, cannot surpass 40'
)
parser.add_argument(
    '--queue_ttl', dest='queue_ttl', default=10,
    help='How many minutes until an operation for an agent is considered expired in the server queue'
)
parser.add_argument(
    '--web_count', dest='web_count', default=1,
    help='The number of vFense_web daemons to run at once, cannot surpass 40'
)
parser.add_argument(
    '--server_cert', dest='server_cert', default='server.crt',
    help='ssl certificate to use, default is to use server.crt'
)
parser.add_argument(
    '--server_key', dest='server_key', default='server.key',
    help='ssl certificate to use, default is to use server.key'
)
parser.add_argument(
    '--cve-data', dest='cve_data', action='store_true',
    help='Initialize CVE data. This is the default.'
)
parser.add_argument(
    '--no-cve-data', dest='cve_data', action='store_false',
    help='Not to initialize CVE data. This is for testing purposes.'
)
parser.set_defaults(cve_data=True)

args = parser.parse_args()

if args.admin_password:
    password_validated = check_password(args.admin_password)
    if not password_validated[0]:
        print (
            'Password failed to meet the minimum requirements.\n' +
            'Uppercase, Lowercase, Numeric, Alphanumeric ' +
            'and a total of 8 characters.\nYour password: %s is %s' %
            (args.admin_password, password_validated[1])
        )
        sys.exit(1)

if args.queue_ttl:
    args.queue_ttl = int(args.queue_ttl)
    if args.queue_ttl < 2:
        args.queue_ttl = 10

if args.dns_name:
    url = 'https://%s/packages/' % (args.dns_name)
    nginx_server_name = args.dns_name
else:
    url = 'https://%s/packages/' % (args.ip_address)
    nginx_server_name = args.ip_address

ncc.nginx_config_builder(
    nginx_server_name,
    args.server_cert,
    args.server_key,
    rvlistener_count=int(args.listener_count),
    rvweb_count=int(args.web_count)
)

def initialize_db():
    os.umask(0)
    if not os.path.exists('/opt/TopPatch/var/tmp'):
        os.mkdir('/opt/TopPatch/var/tmp', 0755)
    if not os.path.exists(RETHINK_CONF):
        subprocess.Popen(
            [
                'ln', '-s',
                RETHINK_SOURCE_CONF,
                RETHINK_CONF
            ],
        )
    if not os.path.exists('/var/lib/rethinkdb/vFense'):
        os.makedirs('/var/lib/rethinkdb/vFense')
        subprocess.Popen(
            [
                'chown', '-R', 'rethinkdb.rethinkdb', '/var/lib/rethinkdb/vFense'
            ],
        )

    if not os.path.exists('/opt/TopPatch/var/log'):
        os.mkdir('/opt/TopPatch/var/log', 0755)
    if not os.path.exists('/opt/TopPatch/var/scheduler'):
        os.mkdir('/opt/TopPatch/var/scheduler', 0755)
    if not os.path.exists('/opt/TopPatch/var/packages'):
        os.mkdir('/opt/TopPatch/var/packages', 0755)
    if not os.path.exists('/opt/TopPatch/logs'):
        os.mkdir('/opt/TopPatch/logs', 0755)
    if not os.path.exists('/opt/TopPatch/var/packages/tmp'):
        os.mkdir('/opt/TopPatch/var/packages/tmp', 0775)
    if not os.path.exists('/opt/TopPatch/tp/src/plugins/vuln/windows/data/xls'):
        os.makedirs('/opt/TopPatch/tp/src/plugins/vuln/windows/data/xls', 0755)
    if not os.path.exists('/opt/TopPatch/tp/src/plugins/vuln/cve/data/xml'):
        os.makedirs('/opt/TopPatch/tp/src/plugins/vuln/cve/data/xml', 0755)
    if not os.path.exists('/opt/TopPatch/tp/src/plugins/vuln/ubuntu/data/html'):
        os.makedirs('/opt/TopPatch/tp/src/plugins/vuln/ubuntu/data/html', 0755)
    if get_distro() in DEBIAN_DISTROS:
        subprocess.Popen(
            [
                'update-rc.d', 'vFense',
                'defaults'
            ],
        )

        if not os.path.exists('/etc/init.d/vFense'):
            subprocess.Popen(
                [
                    'ln', '-s',
                    '/opt/TopPatch/tp/src/daemon/vFense',
                    '/etc/init.d/vFense'
                ],
        )

    if get_distro() in REDHAT_DISTROS:
        if os.path.exists('/usr/bin/rqworker'):
            subprocess.Popen(
                [
                    'ln', '-s',
                    '/usr/bin/rqworker',
                    '/usr/local/bin/rqworker'
                ],
            )

    if os.path.exists(get_sheduler_location()):
        subprocess.Popen(
            [
                'patch', '-N',
                get_sheduler_location(),
                '/opt/TopPatch/conf/patches/scheduler.patch'
            ],
        )
    try:
        tp_exists = pwd.getpwnam('toppatch')

    except Exception as e:
        if get_distro() in DEBIAN_DISTROS:
            subprocess.Popen(
                [
                    'adduser', '--disabled-password', '--gecos', 'GECOS','toppatch',
                ],
            )
        elif get_distro() in REDHAT_DISTROS:
            subprocess.Popen(
                [
                    'useradd', 'toppatch',
                ],
            )

    rethink_start = subprocess.Popen(['service', 'rethinkdb','start'])
    while not db_connect():
        print 'Sleeping until rethink starts'
        sleep(2)
    completed = True
    if completed:
        conn = db_connect()
        r.db_create('toppatch_server').run(conn)
        db = r.db('toppatch_server')
        conn.close()
        ci.initialize_indexes_and_create_tables()
        conn = db_connect()

        customer.create_customer(
            DefaultCustomers.DEFAULT,
            http_application_url_location=url,
            server_queue_ttl=args.queue_ttl,
            init=True
        )
        group_data = group.create_group(
            DefaultGroups.ADMIN,
            DefaultCustomers.DEFAULT,
            [Permissions.ADMINISTRATOR]
        )
        admin_group_id = group_data['generated_ids']
        print group_data
        print admin_group_id
        user.create_user(
            DefaultUser.ADMIN,
            'vFense Admin Account',
            args.admin_password,
            admin_group_id,
            DefaultCustomers.DEFAULT,
            '',
        )
        print 'Admin user and password = admin:%s' % (args.admin_password)
        agent_pass = generate_pass()
        user.create_user(
            DefaultUser.AGENT,
            'vFense Agent Communication Account',
            agent_pass,
            admin_group_id,
            DefaultCustomers.DEFAULT,
            '',
        )
        print 'Agent user and password = agent:%s' % (agent_pass)

        monit.monit_initialization()


        if args.cve_data:
            print "Updating CVE's..."
            load_up_all_xml_into_db()
            print "Done Updating CVE's..."
            print "Updating Microsoft Security Bulletin Ids..."
            parse_bulletin_and_updatedb()
            print "Done Updating Microsoft Security Bulletin Ids..."
            print "Updating Ubuntu Security Bulletin Ids...( This can take a couple of minutes )"
            begin_usn_home_page_processing(full_parse=True)
            print "Done Updating Ubuntu Security Bulletin Ids..."


        conn.close()
        completed = True

        msg = 'Rethink Initialization and Table creation is now complete'
        #rethink_stop = subprocess.Popen(['service', 'rethinkdb','stop'])
        rql_msg = 'Rethink stopped successfully\n'

        return completed, msg
    else:
        completed = False
        msg = 'Failed during Rethink startup process'
        return completed, msg


def clean_database(connected):
    os.chdir(RETHINK_PATH)
    completed = True
    rql_msg = None
    msg = None
    if connected:
        rethink_stop = subprocess.Popen(['service', 'rethinkdb','stop'])
        rql_msg = 'Rethink stopped successfully\n'
    try:
        shutil.rmtree(RETHINK_DATA_PATH)
        msg = 'Rethink instances.d directory removed and cleaned'
    except Exception as e:
        msg = 'Rethink instances.d directory could not be removed'
        completed = False
    if rql_msg and msg:
        msg = rql_msg + msg
    elif rql_msg and not msg:
        msg = rql_msg
    return completed, msg


if __name__ == '__main__':
    conn = db_connect()
    if conn:
        connected = True
        rql_msg = 'Rethink is Running'
    else:
        connected = False
        rql_msg = 'Rethink is not Running'
    print rql_msg
    db_clean, db_msg = clean_database(connected)
    print db_msg
    db_initialized, msg = initialize_db()
    initialized = False
    if db_initialized:
        print 'vFense environment has been succesfully initialized\n'
        subprocess.Popen(
            [
                'chown', '-R', 'toppatch.toppatch', '/opt/TopPatch'
            ],
        )

    else:
        print 'vFense Failed to initialize, please contact TopPatch support'

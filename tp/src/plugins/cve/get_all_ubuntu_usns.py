from BeautifulSoup import BeautifulSoup
import requests
import re
import gc
import sys
import logging
import logging.config
from time import mktime
from datetime import datetime
from vFense.db.client import r

from vFense.utils.common import month_to_num_month
from vFense.plugins.cve import *
from vFense.plugins.cve.cve_constants import *
from vFense.plugins.cve.bulletin_parser import build_bulletin_id
from vFense.plugins.cve.cve_db import insert_into_bulletin_collection_for_ubuntu

MAIN_URL = 'http://www.ubuntu.com'
MAIN_USN_URL = 'http://www.ubuntu.com/usn'
USR_URI = '/usn/usn-[0-9]+[0-9]+'
NEXT_PAGE = '\?page=[0-9]+'

logging.config.fileConfig('/opt/TopPatch/conf/logging.config')
logger = logging.getLogger('cve')

def format_data_to_insert_into_db(
    usn_id, details, cve_ids,
    apps_data, date_posted
    ):

    data_to_insert = []
    for data in apps_data:
        string_to_build_id = ''
        for app in data[UbuntuSecurityBulletinKey.Apps]:
            string_to_build_id = (
                string_to_build_id +
                app['name'] +
                app['version']
            )

        string_to_build_id = (
            string_to_build_id +
            data[UbuntuSecurityBulletinKey.OsString]
        )

        bulletin_id = build_bulletin_id(string_to_build_id)

        data_to_insert.append(
            {
                UbuntuSecurityBulletinKey.Id: bulletin_id,
                UbuntuSecurityBulletinKey.BulletinId: usn_id,
                UbuntuSecurityBulletinKey.Details: details,
                UbuntuSecurityBulletinKey.DatePosted: date_posted,
                UbuntuSecurityBulletinKey.Apps: data[UbuntuSecurityBulletinKey.Apps],
                UbuntuSecurityBulletinKey.OsString: data[UbuntuSecurityBulletinKey.OsString],
                UbuntuSecurityBulletinKey.CveIds: cve_ids
            }
        )

    return(data_to_insert)


def get_cve_info(cve_references):
    cve_ids = []
    for reference in cve_references:
        cve_ids.append(reference.text)
    return(cve_ids)


def parse_multiple_dd_tags(info):
    app_info = []
    while True:
        if 'name' in dir(info):
            if info.name == 'dt' or info.name == 'dl' or info.name == 'dd':
                if info.a:
                    app_info.append(
                        {
                            'name': info.a.text,
                            'version': info.span.a.text
                        }
                    )
                else:
                    app_info.append(
                        {
                            'name': info.contents[0],
                            'version': info.span.text
                        }
                    )

                info = info.findNextSibling()
                if info:
                    if info.name != 'dd':
                        break
                else:
                    break
    return(info, app_info)


def get_app_info(info):
    app_info = []
    while True:
        app_data = {}
        if info.name == 'dt' or info.name == 'dl':
            if info.name == 'dt':
                app_data['os_string'] = info.text.replace(':', '')
                info, app_data['apps'] = (
                    parse_multiple_dd_tags(
                        info.findNextSibling()
                    )
                )

            elif info.name == 'dl':
                app_data['os_string'] = info.dt.text.replace(':', '')
                info, app_data['apps'] = (
                    parse_multiple_dd_tags(info.dd)
                )

            app_info.append(app_data)

            if not info:
                break

    return(app_info)

def get_date_posted(date_em):
    date_posted = u''
    try:
        day, month, year = date_em.text.split()
        day = int(re.sub('[a-zA-Z]+', '', day))
        month = month_to_num_month[re.sub(',', '', month)]
        year = int(year)
        date_posted = (
            r.epoch_time(mktime(datetime(year, month, day).timetuple()))
        )
    except Exception as e:
        logger.exception(e)

    return(date_posted)

def get_details(soup_details):
    details = u''
    while True:
        tag = soup_details.findNext()
        if tag.name != 'h3':
            if tag.name == 'p':
                text = unicode(tag.text).encode(sys.stdout.encoding, 'replace').decode('utf-8')
                details = details + text + '\n\n'
        else:
            break
        soup_details = tag

    #details = unicode(details).encode(sys.stdout.encoding, 'replace')
    return(details)

def write_content_to_file(file_location, url):
    usn_file = open(file_location, 'wb')
    try:
        #print write_content_to_file.func_name, url
        usn_page = requests.get(url)
        usn_page.close()
    except Exception as e:
        write_content_to_file(file_location,url)
    completed = False
    content = None
    if usn_page.ok:
        content = usn_page.content
        #content = unicode(usn_page.text).encode(sys.stdout.encoding, 'replace').decode('utf-8')
        completed = True
        usn_file.write(content)
        usn_file.close()
    return(content, completed)


def get_url_content(usn_uri):
    def get_usn_uri(usn_uri):
        try:
            usn_page = requests.get(usn_uri, timeout=1)
            usn_page.close()
            if usn_page.ok:
                content = usn_page.content
                completed = True

        except Exception as e:
            get_usn_uri(usn_uri)
            completed = False,
            content = None

        return(completed, content)

    content = None
    completed = False
    usn = usn_uri.split('/')[-2]
    usn_file_location = HTML_DIR_UBUNTU + usn
    if os.path.exists(usn_file_location):
        if os.stat(usn_file_location).st_size > 0:
            content = open(usn_file_location, 'r').read()
            completed = True
        else:
            if re.search('http', usn_uri):
                #print get_url_content.func_name, usn_uri
                completed, content = get_usn_uri(usn_uri)

    elif not os.path.exists(usn_file_location):
        if re.search('http', usn_uri):
            #print get_url_content.func_name, usn_uri
            completed, content = get_usn_uri(usn_uri)
            content, completed = (
                write_content_to_file(
                    usn_file_location, MAIN_URL + usn_uri
                )
            )

    return(content, completed)


def process_usn_page(usn_uri):
    content, completed = get_url_content(usn_uri)
    details = ''
    date_posted = ''
    bulletin_id = ''
    app_info = []
    data = []
    cve_references = []
    if content:
        soup = BeautifulSoup(content.replace('<br />', '\n'))
        date_posted_em = soup.find('em')
        bulletin_h2 = soup.div.find('h2')
        details_h3 = soup.div.find('h3', text='Details')
        app_info_dl = soup.div.findAll('dl')
        cve_info_h3 = soup.div.findAll('h3', text='References')
        if date_posted_em:
            date_posted = get_date_posted(date_posted_em)

        if bulletin_h2:
            bulletin_id = bulletin_h2.text.split()[-1]
        else:
            return([], False)

        if details_h3:
            details = get_details(details_h3)
        else:
            return([], False)

        if len(app_info_dl) > 0:
            if len(app_info_dl[0]) > 1:
                app_info = get_app_info(app_info_dl[0])
            else:
                return([], False)

        if len(cve_info_h3) > 0:
            cve_references = (
                get_cve_info(
                    cve_info_h3[0].findAllNext('a', href=re.compile('.*cve'))
                )
            )
        data = (
            format_data_to_insert_into_db(
                bulletin_id, details, cve_references, app_info, date_posted
            )
        )
    return(data, completed)


def begin_usn_home_page_processing(next_page=None, full_parse=False):
    if next_page:
        url = MAIN_USN_URL + '/' + next_page
        #print begin_usn_home_page_processing.func_name, url
        try:
            main_page = requests.get(url, timeout=1)
        except Exception as e:
            return(begin_usn_home_page_processing(next_page, True))
    else:
        #print begin_usn_home_page_processing.func_name, MAIN_USN_URL
        try:
            main_page = requests.get(MAIN_USN_URL)
        except Exception as e:
            return(begin_usn_home_page_processing(full_parse=True))

    try:
        if main_page.ok:
            soup = BeautifulSoup(main_page.content)
            main_page.close()
            next_page = (
                soup.find(
                    'div',
                    { 
                        'class': 'pagination'
                    }
                ).find(
                    'a',
                    {
                        'href': re.compile(NEXT_PAGE)
                    },
                    text=re.compile('Next'),
                )
            )
            usn_uris = (
                soup.find(
                    'div',
                    {
                        'id': 'content'
                    }
                ).findAll(
                    'a',
                    {
                        'href': re.compile(USR_URI)
                    }
                )
            )
            if len(usn_uris) > 0:
                data = []
                for usn_uri in usn_uris:
                    data_to_update, ok = process_usn_page(usn_uri['href'])
                    if ok:
                        data = data + data_to_update
                insert_into_bulletin_collection_for_ubuntu(data)

            if full_parse:
                if next_page:
                    return(begin_usn_home_page_processing(next_page.parent['href'], True))

    except Exception as e:
        logger.exception(e)
    gc.collect()
    logger.info('finished ubuntu usn update process')

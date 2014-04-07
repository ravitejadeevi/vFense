"CVE DOWNLOADER FOR TOPPATCH, NVD/CVE XML VERSION 1.2"
import os
import re
import requests
import logging
import logging.config
from vFense.plugins.vuln.windows._constants import *

logging.config.fileConfig('/opt/TopPatch/conf/logging.config')
logger = logging.getLogger('cve')


def get_msft_bulletin_url():
    """Hack to retrieve the Microsoft XLSX url and name of the file.
    """
    xls_url = None
    xls_file_name = None

    main_url = requests.get(WindowsBulletinStrings.XLS_DOWNLOAD_URL)
    if main_url.status_code == 200:
        xls_url = re.search('http.*.xlsx', main_url.content).group()
        if xls_url:
            xls_file_name = xls_url.split('/')[-1]

    return(xls_url, xls_file_name)


def download_latest_xls_from_msft():
    """Download the lates Microsoft Security Bulletin excel spreadsheet
        and than store it on disk
    Returns:
        Tuple (Boolen, file_location)
    """
    downloaded = True
    xls_file_location = None
    if not os.path.exists(WindowsDataDir.XLS_DIR):
        os.makedirs(WindowsDataDir.XLS_DIR)
    xls_url, xls_file_name = get_msft_bulletin_url()
    if xls_url:
        xls_file_location = WindowsDataDir.XLS_DIR+'/'+xls_file_name
        xls_data = requests.get(xls_url)
        if xls_data.ok:
            xml_file = open(xls_file_location, 'wb')
            xml_file.write(xls_data.content)
            xml_file.close()
            if (xls_data.headers['content-length'] ==
                    str(os.stat(xls_file_location).st_size)):
                logger.info(
                    '%s downloaded to %s: file_size: %s matches content-length' %
                    (
                        xls_url,xls_file_location,
                        os.stat(xls_file_location).st_size
                    )
                )
            else:
                downloaded = False
                logger.warn(
                    '%s downloaded to %s: file_size: %s does not match the content-length' %
                    (
                        xls_url,xls_file_location,
                        os.stat(xls_file_location).st_size
                    )
                )
    return(downloaded, xls_file_location)

#download_latest_xls_from_msft()

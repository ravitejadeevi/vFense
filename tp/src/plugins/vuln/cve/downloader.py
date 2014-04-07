"CVE DOWNLOADER FOR TOPPATCH, NVD/CVE XML VERSION 1.2"
import os
import requests
import logging
import logging.config
from vFense.plugins.vuln.cve._constants import *
from vFense.plugins.vuln._constants import *

logging.config.fileConfig('/opt/TopPatch/conf/logging.config')
logger = logging.getLogger('cve')


def cve_downloader(url, file_path):
    """Http Downloader, that returns the status of the download
        and the size of the file
    Args:
        url (str): the full url path of the xml file.
        file_path (str): The full file patch, to where it is going to be saved.

    Basic Usage:
        >>> from vFense.plugins.vuln.cve.downloader import cve_downloader
        >>> cve_downloader

    Returns:
        Tuple (Boolean, file_size)
        (True, 186)
    """
    r = requests.get(url)
    xml = open(file_path, 'wb')
    if r.ok:
        xml.write(r.content)

    xml.close()

    return(r.ok, os.stat(file_path).st_size)

def log_status(status, size, url_path, nvd_path):
    """Log the status of the downloaded cve file
    Args:
        status (bool): True or False (Verify if the file downloaded)
        size (int): The size of the file that was downloaded.
        url_path (str): The full url of the file that was downloaded.
        nvd_path (str): The full path on disk of the file that was downloaded.

    """
    if status == True and size > 0:
        msg = '%s Downloaded to %s' % ( url_path, nvd_path )
        logger.info(msg)
    elif status == False:
        msg =  '%s Could not be downloaded' % ( url_path )
        logger.warn(msg)
    else:
        msg = '%s Was downloaded to %s, but the size is %d' \
                % ( url_path, nvd_path, size )
        logger.error(msg)

def start_nvd_xml_download():
    """The is the CVE/NVD Downloader
    Basic Usage:
        >>> from vFense.plugins.vuln.cve.downloader import start_nvd_xml_download
        >>> start_nvd_xml_download()
    """
    iter_year = CVEStrings.START_YEAR
    if not os.path.exists(CVEDataDir.XML_DIR):
        os.makedirs(CVEDataDir.XML_DIR, 0755)
    xml_status = (
        cve_downloader(
            CVEStrings.NVD_MODIFIED_URL,
            CVEDataDir.NVD_MODIFIED_FILE
        )
    )
    log_status(
        xml_status[0], xml_status[1],
        CVEStrings.NVD_MODIFIED_URL, 
        CVEDataDir.NVD_MODIFIED_FILE
    )

    """
    If we have not yet downloaded the 2002 until now CVE's,
    please download then now
    """
    while iter_year <= DateValues.CURRENT_YEAR:
        nvd = CVEStrings.NVDCVE_BASE + str(iter_year) + '.xml'
        full_url =  CVEStrings.NVD_DOWNLOAD_URL + nvd
        full_nvd = os.path.join(CVEDataDir.XML_DIR, nvd)
        if not os.path.exists(full_nvd):
            xml_status = cve_downloader(full_url, full_nvd)
            log_status(xml_status[0], xml_status[1], full_url, full_nvd)
        
        elif iter_year == DateValues.CURRENT_YEAR:
            "Always download the latest and the current year"
            xml_status = cve_downloader(full_url, full_nvd)
            log_status(xml_status[0], xml_status[1], full_url, full_nvd)

        else:
            msg = "%s already exists at %s" % ( nvd, full_nvd )
            logger.info(msg)
        iter_year = iter_year + 1

import sys
import logging
import logging.config

from vFense.core.decorators import return_status_tuple, time_it
from vFense.db.client import db_create_close, r
from vFense.plugins.vuln._constants import *
from vFense.plugins.vuln.windows import *
from vFense.plugins.vuln.windows._constants import *

logging.config.fileConfig('/opt/TopPatch/conf/logging.config')
logger = logging.getLogger('cve')


@time_it
@db_create_close
def fetch_vuln_ids(kb, conn=None):
    """Retrieve Windows Bulletin IDS and CVE_IDS for an Application
    Args:
        kb (str): The KB number of the application (KB980436)

    Basic Usage:
        >>> from vFense.plugins.vuln.windows._db import fetch_windows_vuln_ids
        >>> kb = 'KB980436'
        >>> fetch_ubuntu_vuln_ids(kb)

    Returns:
        Dictionary
        {
            "cve_ids": [
                "CVE-2009-3555", 
                "CVE-2010-2566"
            ], 
            "bulletin_id": "MS10-049"
        }
    """
    data = {}
    try:
        data = list(
            r
            .table(WindowsSecurityCollection.Bulletin)
            .get_all(kb, index=WindowsSecurityBulletinIndexes.ComponentKb)
            .pluck(WindowsSecurityBulletinKey.BulletinId, WindowsSecurityBulletinKey.CveIds)
            .run(conn)
        )

    except Exception as e:
        logger.exception(e)

    return(data)

@time_it
@db_create_close
def fetch_vuln_data(vuln_id, conn=None):
    """Retrieve Windows Bulletin data for an Application by bulletin id.
    Args:
        vuln_id (str): The vulnerability id aka (MS10-049)

    Basic Usage:
        >>> from vFense.plugins.vuln.windows._db import fetch_vuln_data
        >>> vuln_id = 'MS10-049'
        >>> fetch_vuln_data(vuln_id)

    Returns:
    {
        "bulletin_details": "Vulnerabilities in SChannel could allow Remote Code Execution", 
        "supercedes": [
            {
                "supercedes_bulletin_kb": "KB960225", 
                "supercedes_bulletin_id": "MS09-007"
            }
        ], 
        "id": "03639df1f16464ef9defe6d1735fd032432befdbd325ab4bb24993fc58f287ea", 
        "cve_ids": [
            "CVE-2009-3555", 
            "CVE-2010-2566"
        ], 
        "bulletin_id": "MS10-049", 
        "date_posted": 1281423600
    }
    """
    data = []
    map_hash = (
        {
            WindowsSecurityBulletinKey.Id: r.row[WindowsSecurityBulletinKey.Id],
            WindowsSecurityBulletinKey.BulletinId: r.row[WindowsSecurityBulletinKey.BulletinId],
            WindowsSecurityBulletinKey.DatePosted: r.row[WindowsSecurityBulletinKey.DatePosted].to_epoch_time(),
            WindowsSecurityBulletinKey.Details: r.row[WindowsSecurityBulletinKey.Details],
            WindowsSecurityBulletinKey.CveIds: r.row[WindowsSecurityBulletinKey.CveIds],
            WindowsSecurityBulletinKey.Supersedes: r.row[WindowsSecurityBulletinKey.Supersedes],
        }
    )
    try:
        data = list(
            r
            .table(WindowsSecurityCollection.Bulletin)
            .get_all(vuln_id, index=WindowsSecurityBulletinIndexes.BulletinId)
            .map(map_hash)
            .run(conn)
        )

    except Exception as e:
        logger.exception(e)

    return(data)


@time_it
@db_create_close
@return_status_tuple
def insert_bulletin_data(bulletin_data, conn=None):
    """Insert Windows Bulletin data into the Windows Security Bulletin Collection
        DO NOT CALL DIRECTLY
    Args:
        bulletin_data (list|dict): List or dictionary of vulnerability data

    Basic Usage:
        >>> from vFense.plugins.vuln.windows._db insert_into_bulletin_collection
        >>> insert_into_bulletin_collection([{"bulletin_data goes in here"}])

    Returns:
        Tuple (status_code, count, error, generated ids)
        >>> (2001, 1, None, [])
    """
    data = {}
    try:
        data = (
            r
            .table(WindowsSecurityCollection.Bulletin)
            .insert(bulletin_data, upsert=True)
            .run(conn)
        )

    except Exception as e:
        logger.exception(e)

    return(data)

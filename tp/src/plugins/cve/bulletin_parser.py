import os
import re
import sys
import gc
from time import mktime
from datetime import datetime
import logging
import logging.config

from time import mktime
from datetime import datetime
from hashlib import sha256
from re import sub

from xlrd import open_workbook, xldate_as_tuple

from vFense.plugins.cve import *
from vFense.plugins.cve.cve_constants import *
from vFense.plugins.cve.cve_db import insert_into_bulletin_collection_for_windows
from vFense.plugins.cve.downloader import download_latest_xls_from_msft
from vFense.db.client import r

logging.config.fileConfig('/opt/TopPatch/conf/logging.config')
logger = logging.getLogger('cve')

def build_bulletin_id(data):
    return (sha256(data).hexdigest())

def parse_spread_sheet(bulletin_file):
    bulletin_list = []
    workbook = open_workbook(bulletin_file)
    sheet = workbook.sheet_by_name(WORKBOOK_SHEET)
    rows = range(sheet.nrows)
    rows.pop(0)
    for i in rows:
        row = sheet.row_values(i)
        bulletin_dict = {}
        supercede_list = []
        if row[7] != '':
            row[7] = 'KB' + str(int(row[7]))

        if row[2] != '':
            row[2] = 'KB' + str(int(row[2]))

        rows_to_use = (
            row[1] + row[2] + row[3] + row[4] +
            row[6] + row[7] + row[8] + row[9]
        )
        rows_to_use = unicode(rows_to_use).encode(sys.stdout.encoding, 'replace')
        id = build_bulletin_id(rows_to_use)
        bulletin_dict[WindowsSecurityBulletinKey.Id] = id
        date = xldate_as_tuple(row[0], workbook.datemode)
        epoch_time = mktime(datetime(*date).timetuple())
        bulletin_dict[WindowsSecurityBulletinKey.DatePosted] = (
            r.epoch_time(epoch_time)
        )
        bulletin_dict[WindowsSecurityBulletinKey.BulletinId] = row[1]
        bulletin_dict[WindowsSecurityBulletinKey.BulletinKb] = row[2]
        bulletin_dict[WindowsSecurityBulletinKey.BulletinSeverity] = row[3]
        bulletin_dict[WindowsSecurityBulletinKey.BulletinImpact] = row[4]
        bulletin_dict[WindowsSecurityBulletinKey.Details] = row[5]
        bulletin_dict[WindowsSecurityBulletinKey.AffectedProduct] = row[6]
        bulletin_dict[WindowsSecurityBulletinKey.ComponentKb] = row[7]
        bulletin_dict[WindowsSecurityBulletinKey.AffectedComponent] = row[8]
        bulletin_dict[WindowsSecurityBulletinKey.ComponentImpact] = row[9]
        bulletin_dict[WindowsSecurityBulletinKey.ComponentSeverity] = row[10]
        if row[12] != '':
            info = row[12].split(',')
            for j in info:
                bulletin_data = j.split('[')
                if len(bulletin_data) > 1:
                    bulletin_id = bulletin_data[0]
                    bulletin_kb = re.sub('^', 'KB', bulletin_data[1][:-1])
                else:
                    bulletin_id = bulletin_data[0]
                    bulletin_kb = None

                supercede_list.append(
                    {
                        WindowsSecurityBulletinKey.SupersedesBulletinId: bulletin_id,
                        WindowsSecurityBulletinKey.SupersedesBulletinKb: bulletin_kb
                    }
                )
        bulletin_dict[WindowsSecurityBulletinKey.Supersedes] = supercede_list
        bulletin_dict[WindowsSecurityBulletinKey.Reboot] = row[13]
        bulletin_dict[WindowsSecurityBulletinKey.CveIds] = row[14].split(',')
        bulletin_list.append(bulletin_dict)

    return(bulletin_list)

def parse_bulletin_and_updatedb():
    logger.info('starting microsoft security bulletin update process')
    if not os.path.exists(XLS_DIR):
        os.makedirs(XLS_DIR)
    downloaded, xls_file = download_latest_xls_from_msft()
    if downloaded:
        bulletin_data = parse_spread_sheet(xls_file)
        insert_into_bulletin_collection_for_windows(bulletin_data)

    logger.info('finished microsoft security bulletin update process')
    gc.collect()

#parse_bulletin_and_updatedb()

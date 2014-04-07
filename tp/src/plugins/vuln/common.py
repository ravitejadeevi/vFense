import logging
import logging.config
from hashlib import sha256


logging.config.fileConfig('/opt/TopPatch/conf/logging.config')
logger = logging.getLogger('cve')

def build_bulletin_id(data):
    return (sha256(data).hexdigest())

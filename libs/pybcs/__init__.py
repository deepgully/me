try:
    from bae.api import logging
except:
    import logging
    from httpc import logger
    def init_logging(set_level = logging.INFO, 
                 console = True,
                 log_file_path = None):
        common.init_logging(httpc.logger, set_level, console, log_file_path)
    
from bcs import BCS
from bucket import Bucket

#modules should import
__all__ = ['bcs', 'bucket', 'object']


from common import NotImplementException
from common import md5_for_file

from httpc import *
import common, httpc


#init_logging(logging.INFO, True, log_file_path='log/bcs.log')



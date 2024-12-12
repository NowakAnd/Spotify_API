import logging
from datetime import datetime as dt

logging.basicConfig(filename="logs/" + dt.now().strftime('log%H_%M_%d_%m_%Y.log'),
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', filemode='w',
                    level='INFO')

logger = logging.getLogger(__name__)
logger.info("LOGS START")

def function_logging(func):
    def wrapper(*args, **kwargs):
        logger.info("START "+ func.__name__)
        ret = func(*args, **kwargs)
        logger.info("END " + func.__name__)
        return ret
    return wrapper
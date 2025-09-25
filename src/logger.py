import logging
import colorlog

# Create a custom formatter with colors
formatter = colorlog.ColoredFormatter(
    "%(log_color)s%(asctime)s - %(levelname)s - %(message)s",
    datefmt=None,
    reset=True,
    log_colors={
        'DEBUG': 'cyan',
        'INFO': 'green',
        'WARNING': 'yellow',
        'ERROR': 'red',
        'CRITICAL': 'red,bg_white',
    },
    secondary_log_colors={},
    style='%'
)

# Create console handler and set level to debug
console = logging.StreamHandler()
console.setLevel(logging.INFO)
console.setFormatter(formatter)

# Get logger and add the console handler
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logger.addHandler(console)
logger.propagate = False  # Prevents duplicate logs if other loggers are configured

logger.info("LOGS START")

def function_logging(func):
    def wrapper(*args, **kwargs):
        logger.info("START "+ func.__name__)
        ret = func(*args, **kwargs)
        logger.info("END " + func.__name__)
        return ret
    return wrapper
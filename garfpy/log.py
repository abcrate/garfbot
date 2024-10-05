import logging
from logging.handlers import TimedRotatingFileHandler

logger = logging.getLogger('garflog')
logger.setLevel(logging.INFO)
formatter=logging.Formatter(
    '%(asctime)s [%(levelname)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
    )
file_handler = TimedRotatingFileHandler(
    'garfbot.log',
    when='midnight',
    interval=1,
    backupCount=7,
    delay=True # Counter-intuitively, this will flush output immediately
    )
file_handler.setFormatter(formatter)
console_handler = logging.StreamHandler()
console_handler.setFormatter(formatter)
logger.addHandler(file_handler)
logger.addHandler(console_handler)

if not logger.hasHandlers():
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

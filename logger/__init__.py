import logging
from settings import DEBUG


logging.basicConfig()
logger = logging.getLogger()

if DEBUG:
    logger.setLevel(logging.DEBUG)
else:
    logger.setLevel(logging.INFO)
    logging.getLogger("asyncssh").setLevel(logging.WARNING)

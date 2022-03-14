import logging
from settings import DEBUG


logging.basicConfig()
logger = logging.getLogger()

if DEBUG:
    logger.setLevel(logging.DEBUG)
    logging.getLogger("asyncssh").setLevel(logging.WARNING)

else:
    logger.setLevel(logging.INFO)
    logging.getLogger("asyncssh").setLevel(logging.WARNING)

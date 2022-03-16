import logging
from settings import DEBUG


logging.basicConfig(
    filename="logfile.txt",
    filemode="a",
    format='[%(levelname)s][%(asctime)s](%(name)s) - %(message)s',
    datefmt='%x %X'
)
logger = logging.getLogger()

if DEBUG:
    logger.setLevel(logging.DEBUG)
    logging.getLogger("asyncssh").setLevel(logging.DEBUG)
else:
    logger.setLevel(logging.INFO)
    logging.getLogger("asyncssh").setLevel(logging.WARNING)

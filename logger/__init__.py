import logging
from settings import DEBUG


def init_logger():
    logging.basicConfig(
        # filename="logfile.txt",
        # filemode="a",
        format="%(pathname)s:%(lineno)d in %(funcName)s\n[%(levelname)s][%(asctime)s](%(name)s) - %(message)s",
        datefmt="%x %X",
    )
    _logger = logging.getLogger()

    if DEBUG:
        _logger.setLevel(logging.DEBUG)
        logging.getLogger("asyncssh").setLevel(logging.DEBUG)
    else:
        _logger.setLevel(logging.WARNING)
        logging.getLogger("asyncssh").setLevel(logging.WARNING)

    return _logger


logger = init_logger()

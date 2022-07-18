import logging
from pyasic.settings import PyasicSettings


def init_logger():
    if PyasicSettings().logfile:
        logging.basicConfig(
            filename="logfile.txt",
            filemode="a",
            format="%(pathname)s:%(lineno)d in %(funcName)s\n[%(levelname)s][%(asctime)s](%(name)s) - %(message)s",
            datefmt="%x %X",
        )
    else:
        logging.basicConfig(
            format="%(pathname)s:%(lineno)d in %(funcName)s\n[%(levelname)s][%(asctime)s](%(name)s) - %(message)s",
            datefmt="%x %X",
        )

    _logger = logging.getLogger()

    if PyasicSettings().debug:
        _logger.setLevel(logging.DEBUG)
        logging.getLogger("asyncssh").setLevel(logging.DEBUG)
    else:
        _logger.setLevel(logging.WARNING)
        logging.getLogger("asyncssh").setLevel(logging.WARNING)

    return _logger


logger = init_logger()

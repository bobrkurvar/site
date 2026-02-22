import logging
import sys

# logger = logging.getLogger()
#
# logging.getLogger("asyncio").propagate = False
# logging.getLogger("python_multipart").setLevel(logging.WARNING)
# logger.setLevel(logging.DEBUG)
# formatter = logging.Formatter(
#     "[%(asctime)s] #%(levelname)-8s %(filename)s:%(lineno)d - %(name)s - %(message)s"
# )
#
# console_handler = logging.StreamHandler(sys.stdout)
# console_handler.setLevel(logging.DEBUG)
# console_handler.setFormatter(formatter)
#
# logger.addHandler(console_handler)

class IgnoreFilter(logging.Filter):
    def filter(self, record):
        ignore = {"asyncio"}
        if record.levelno >= logging.WARNING:
            return True
        pocket = record.name.split(".")[0]
        if pocket in ignore:
            return False
        return True


def setup_logging():
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    formatter = logging.Formatter(
        "[%(asctime)s] #%(levelname)-8s %(filename)s:%(lineno)d - %(name)s - %(message)s"
    )

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.DEBUG)
    console_handler.setFormatter(formatter)

    if not any(isinstance(h, logging.StreamHandler) for h in logger.handlers):
        # console_handler.addFilter(IgnoreFilter())
        logger.addHandler(console_handler)
    logging.getLogger("asyncio").setLevel(logging.WARNING)

    logger.addFilter(IgnoreFilter())
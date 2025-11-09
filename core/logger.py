import logging
import sys

logger = logging.getLogger()
# logging.getLogger("aiogram").setLevel()
logging.getLogger("asyncio").propagate = False
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter(
    "[%(asctime)s] #%(levelname)-8s %(filename)s:%(lineno)d - %(name)s - %(message)s"
)

console_handler = logging.StreamHandler(sys.stdout)
console_handler.setLevel(logging.DEBUG)
console_handler.setFormatter(formatter)

logger.addHandler(console_handler)

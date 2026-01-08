import logging
from multiprocessing import Manager
import core.logger

_manager = None
_task_queue = None

log = logging.getLogger(__name__)

def get_task_queue():
    """Получаем очередь задач с ленивой инициализацией"""
    global _manager, _task_queue

    if _manager is None:
        _manager = Manager()
        _task_queue = _manager.Queue(maxsize=100)
        log.debug("QUEUE CREATED")

    return _task_queue

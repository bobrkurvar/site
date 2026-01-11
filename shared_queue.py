import logging
from multiprocessing.managers import BaseManager
from multiprocessing import Queue

log = logging.getLogger(__name__)


if __name__ == "__main__":
    real_queue = Queue(maxsize=100)

    class QueueManager(BaseManager):
        pass

    QueueManager.register('get_queue', callable=lambda: real_queue)

    manager = QueueManager(
        address=('localhost', 50000),  # ← ФИКСИРОВАННЫЙ АДРЕС!
        authkey=b'secret-key'
    )

    # 3. Запускаем сервер
    log.info("Сервер запущен на localhost:50000")
    server = manager.get_server()
    server.serve_forever()

else:
    class ClientManager(BaseManager):
        pass


    _queue_proxy = None

    def get_task_queue():
        global _queue_proxy

        if _queue_proxy is None:
            ClientManager.register('get_queue')

            manager = ClientManager(
                address=('localhost', 50000),  # ← Тот же адрес!
                authkey=b'secret-key'  # ← Тот же ключ!
            )

            try:
                manager.connect()
                _queue_proxy = manager.get_queue()
                log.info("Подключились к серверу очереди")
            except ConnectionRefusedError:
                log.error("Сервер очереди не запущен!")
                raise

        return _queue_proxy
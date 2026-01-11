import asyncio
import concurrent.futures
import logging
import multiprocessing

import core.logger
from services.images import generate_image_variant
from shared_queue import get_task_queue

log = logging.getLogger(__name__)

NUM_WORKERS = 4  # процессов для CPU
MAX_IN_FLIGHT = 8  # сколько задач одновременно в системе
MAX_RETRIES = 3
QUEUE_TIMEOUT = 1.0


async def queue_reader(mp_queue, async_queue, stop_event):
    """
    Единственное место в программе, где мы:
    - трогаем multiprocessing.Queue
    - используем run_in_executor(None, ...)
    """

    loop = asyncio.get_running_loop()

    while not stop_event.is_set():
        try:
            task = await loop.run_in_executor(
                None,
                mp_queue.get,
                True,
                QUEUE_TIMEOUT,
            )
            await async_queue.put(task)

        except multiprocessing.queues.Empty:
            # mp_queue пустая — это нормально
            await asyncio.sleep(0.1)


async def handle_task(executor, task, mp_queue, semaphore):
    input_path, target, quality, retry = task

    async with semaphore:
        try:
            loop = asyncio.get_running_loop()
            await loop.run_in_executor(
                executor,
                generate_image_variant,
                input_path,
                target,
                quality,
            )
            log.info("Task completed: %s", task)

        except Exception as e:
            log.error("Task failed %s: %s", task, e)

            if retry < MAX_RETRIES:
                mp_queue.put((input_path, target, quality, retry + 1))
            else:
                log.critical("Retries exceeded: %s", task)


async def worker_loop(mp_queue):
    stop_event = asyncio.Event()

    # Внутренняя asyncio-очередь
    async_queue = asyncio.Queue(maxsize=MAX_IN_FLIGHT)

    # Ограничение одновременных задач
    semaphore = asyncio.Semaphore(MAX_IN_FLIGHT)

    executor = concurrent.futures.ProcessPoolExecutor(max_workers=NUM_WORKERS)

    reader_task = asyncio.create_task(queue_reader(mp_queue, async_queue, stop_event))

    active_tasks = set()

    try:
        while True:
            task = await async_queue.get()

            t = asyncio.create_task(handle_task(executor, task, mp_queue, semaphore))

            active_tasks.add(t)
            t.add_done_callback(active_tasks.discard)

    except (KeyboardInterrupt, asyncio.CancelledError):
        log.info("Shutdown requested")

    finally:
        # Останавливаем чтение внешней очереди
        stop_event.set()
        reader_task.cancel()

        # Дожидаемся завершения активных задач
        for t in active_tasks:
            t.cancel()

        await asyncio.gather(*active_tasks, return_exceptions=True)

        executor.shutdown(wait=True, cancel_futures=True)
        log.info("Worker stopped")


if __name__ == "__main__":
    multiprocessing.set_start_method("spawn", force=True)

    mp_queue = get_task_queue()
    log.info("IMAGE WORKER START")

    try:
        asyncio.run(worker_loop(mp_queue))
    except KeyboardInterrupt:
        log.info("Process interrupted")

    log.info("IMAGE WORKER END")

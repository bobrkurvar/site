import asyncio
import concurrent.futures
import multiprocessing
from services.images import generate_image_variant
import core.logger
import logging
import psutil  # Для мониторинга процессов
from shared_queue import get_task_queue

log = logging.getLogger(__name__)

task_queue = None


MAX_RETRIES = 3  # Макс. попыток для задачи
MONITOR_INTERVAL = 10  # Секунды между проверками пула
NUM_WORKERS = 4  # Кол-во процессов в пуле

async def process_task(executor, task, task_queue):
    """Асинхронно запускает задачу в executor'е с ретраями"""
    input_path, target, quality, retry_count = task
    log.debug("TASK: input_path: %s", input_path)
    try:
        loop = asyncio.get_running_loop()
        result = await loop.run_in_executor(executor, generate_image_variant, input_path, target, quality)
        log.info(f"Task completed: {task}")
        return result
    except Exception as e:
        log.error(f"Task failed: {task}, error: {e}")
        if retry_count < MAX_RETRIES:
            retry_task = (input_path, target, quality, retry_count + 1)
            task_queue.put(retry_task)  # Перекидываем обратно в queue
            log.info(f"Retrying task: {retry_task}")
        else:
            log.critical(f"Task max retries exceeded: {task}")
        raise

async def monitor_pool(executor):
    """Мониторит процессы в пуле, рестартует при краше"""
    while True:
        await asyncio.sleep(MONITOR_INTERVAL)
        try:
            # Проверяем процессы executor'а
            for proc in executor._processes.values():
                p = psutil.Process(proc.pid)
                if p.status() == psutil.STATUS_ZOMBIE or not p.is_running():
                    log.warning(f"Detected dead process {proc.pid}, restarting pool")
                    executor.shutdown(wait=True)
                    executor = concurrent.futures.ProcessPoolExecutor(max_workers=NUM_WORKERS)
                    log.info("Pool restarted")
                    break  # После рестарта выходим из цикла проверки
        except Exception as e:
            log.error(f"Monitor error: {e}")

async def worker_loop(task_queue):
    """Основной asyncio loop: читает queue, запускает задачи, мониторит"""
    executor = concurrent.futures.ProcessPoolExecutor(max_workers=NUM_WORKERS)
    monitor_task = asyncio.create_task(monitor_pool(executor))  # Запускаем мониторинг
    while True:
        try:
            # Асинхронно ждём задачу из queue (с таймаутом, чтобы не блокировать)
            task = await asyncio.get_running_loop().run_in_executor(None, task_queue.get, True, 1.0)
            asyncio.create_task(process_task(executor, task, task_queue))  # Асинхронно запускаем
        except multiprocessing.queues.Empty:
            await asyncio.sleep(0.1)  # Короткий sleep, если queue пустая
        except Exception as e:
            log.error(f"Worker error: {e}")
            await asyncio.sleep(1)  # Backoff

if __name__ == "__main__":
    task_queue = get_task_queue()
    log.info("IMAGE WORKER START")
    asyncio.run(worker_loop(task_queue))
    log.info("IMAGE WORKER END")
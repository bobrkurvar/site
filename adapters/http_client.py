import logging
from functools import wraps

from httpx import ASGITransport, AsyncClient, ConnectError, HTTPStatusError

log = logging.getLogger(__name__)


def handle_ext_api(func):
    @wraps(func)
    async def wrapper(self, *args, **kwargs):
        try:
            return await func(self, *args, **kwargs)
        except ConnectError:
            log.warning("поключение не установлено")

    return wrapper


def add_exception_handler(cls):
    api_methods = ["generate_image"]
    for attr_name in dir(cls):
        attr = getattr(cls, attr_name)
        if attr in api_methods:
            setattr(cls, attr_name, handle_ext_api(attr))
    return cls


@add_exception_handler
class HttpClient:

    def __init__(self, url=None, app=None):
        self._url = url
        self._app = app
        self._client = (
            AsyncClient(transport=ASGITransport(app=self._app), base_url=self._url)
            if self._app
            else AsyncClient(base_url=self._url)
        )

    @property
    def client(self):
        if self._client is None:
            raise RuntimeError("HTTP client is not initialized")
        return self._client

    async def generate_images(self, **data):
        try:
            resp = await self.client.post("/generate-images", json=data)
            resp.raise_for_status()
            return resp.json()
        except HTTPStatusError as exc:
            log.exception(f"HTTP ошибка: {exc}")
            return None

    async def close(self):
        if self._client:
            await self.client.aclose()
            self._client = None

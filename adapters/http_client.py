import logging
from functools import wraps

from httpx import ASGITransport, AsyncClient, ConnectError, HTTPStatusError

from core import conf

# from aiohttp import ClientResponseError, ClientSession
# from aiohttp.client_exceptions import ClientConnectorError


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


# @add_exception_handler
# class MyExternalApiForBot:
#     def __init__(self, url):
#         self._url = url
#         self._session = None
#
#     async def generate_images(self, **data):
#         async with self._session.post(self._url + "generate-images", json=data) as resp:
#             try:
#                 resp.raise_for_status()
#                 return await resp.json()
#             except ClientResponseError as exc:
#                 log.exception(exc)
#                 return None
#
#     def connect(self):
#         if not self._session:
#             self._session = ClientSession()
#
#     async def close(self):
#         if self._session:
#             log.warning(f"закрываю сессию {self.__class__.__name__}")
#             await self._session.close()
#             self._session = None


class MyExternalApiForBot:
    def __init__(self, url=None, app=None):
        self._url = url
        self._app = app
        self._client = None

    def connect(self):
        if not self._client:
            self._client = (
                AsyncClient(transport=ASGITransport(app=self._app), base_url=self._url)
                if self._app
                else AsyncClient(base_url=self._url)
            )

    async def generate_images(self, **data):
        try:
            resp = await self._client.post("/generate-images", json=data)
            resp.raise_for_status()
            return resp.json()
        except HTTPStatusError as exc:
            log.exception(f"HTTP ошибка: {exc}")
            return None

    async def close(self):
        if self._client:
            await self._client.aclose()
            self._client = None


# url = conf.image_service_url
_http_client: MyExternalApiForBot | None = None


def get_http_client(app=None):
    global _http_client
    if _http_client is None:
        _http_client = MyExternalApiForBot(f"http://{conf.image_service_url}/", app)
    return _http_client

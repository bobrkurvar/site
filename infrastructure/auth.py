import logging
from typing import Annotated

from fastapi import Depends, Request

from infrastructure.crud import Crud, get_db_manager
from infrastructure.user_agent import TokensManager
#from core import conf
from domain import AccessTokenNotExistsError
from services.auth import check_access_token
from .user_agent import fingerPrintDep


log = logging.getLogger(__name__)


# def get_user_from_token(request: Request, fp: fingerPrintDep):
#     log.debug("Starting get_user_from_token")
#     tokens_manager = TokensManager(request=request)
#     token = tokens_manager.get_access_token()
#     if token is None:
#         raise AccessTokenNotExistsError
#     log.debug("token %s", token)
#     payload = check_access_token(token, fp)
#     return payload
#
#
# getUserFromTokenDep = Annotated[dict, Depends(get_user_from_token)]
# dbManagerDep = Annotated[Crud, Depends(get_db_manager)]

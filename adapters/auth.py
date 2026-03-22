import logging
from datetime import timedelta
from typing import Annotated

import jwt
from fastapi import Depends, Request, Response
from fastapi.security.oauth2 import OAuth2PasswordBearer

from adapters.crud import Crud, get_db_manager
from core import conf
from domain import (AccessTokenExpireError, Admin, CredentialsValidateError,
                    InvalidAccessTokenError, NotFoundError,
                    RefreshTokenExpireError)
from services.auth import create_access_token, create_refresh_token
from services.security import verify

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login", auto_error=False)
secret_key = conf.secret_key
algorithm = conf.algorithm
log = logging.getLogger(__name__)


def get_user_from_token(token: Annotated[str, Depends(oauth2_scheme)]):
    log.debug("Starting get_user_from_token")
    try:
        log.debug("token %s", token)
        payload = jwt.decode(token, secret_key, algorithms=algorithm)
        log.debug("Decoded payload: %s", payload)
        user_id = payload.get("sub")
        roles = payload.get("roles")
        if user_id is None:
            log.debug("user_id is None")
            raise InvalidAccessTokenError
        user = {"user_id": int(user_id), "roles": roles}
    except jwt.ExpiredSignatureError:
        raise AccessTokenExpireError
    except jwt.InvalidTokenError:
        raise InvalidAccessTokenError
    return user


getUserFromTokenDep = Annotated[dict, Depends(get_user_from_token)]
dbManagerDep = Annotated[Crud, Depends(get_db_manager)]

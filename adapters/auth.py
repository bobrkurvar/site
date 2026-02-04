import logging
import jwt
from fastapi import Request
from domain.exceptions import UnauthorizedError
from core import config

secret_key = config.secret_key
algorithm = config.algorithm
log = logging.getLogger(__name__)


def get_user_from_token(request: Request):
    token = request.cookies.get("access_token")
    log.debug("Starting get_user_from_token")
    try:
        log.debug("token %s", token)
        payload = jwt.decode(token, secret_key, algorithms=algorithm)
        log.debug("Decoded payload: %s", payload)
        username = payload.get("sub")
        if username is None:
            log.debug("username is None")
            raise UnauthorizedError(validate=True)
    except jwt.ExpiredSignatureError:
        raise UnauthorizedError(refresh_token=True)
    except jwt.InvalidTokenError:
        raise UnauthorizedError(access_token=True)
    return username


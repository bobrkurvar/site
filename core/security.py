#
# import logging
# #from datetime import datetime, timedelta, timezone
# #from typing import Annotated
#
# import jwt
# from fastapi import Request
# #from fastapi.security.oauth2 import OAuth2PasswordBearer
# from api.exceptions.errors import UnauthorizedError
# #import bcrypt
#
# from core import config
#
# #oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login", auto_error=False)
# secret_key = config.secret_key
# algorithm = config.algorithm
# log = logging.getLogger(__name__)
#
#
# # def get_password_hash(password: str) -> str:
# #     hash_password = bcrypt.hash(password)
# #     return hash_password
# #
# #
# # def verify(plain_password: str, password_hash: str) -> bool:
# #     return bcrypt.verify(plain_password, password_hash)
#
# # def get_password_hash(password: str) -> str:
# #     salt = bcrypt.gensalt()
# #     hashed = bcrypt.hashpw(password.encode(), salt)
# #     return hashed.decode()
# #
# # def verify(password: str, hashed: str) -> bool:
# #     return bcrypt.checkpw(password.encode(), hashed.encode())
# #
# #
# #
# #
# # def create_access_token(data: dict, expires_delta: timedelta = None) -> str:
# #     to_encode = data.copy()
# #     expire = (
# #         datetime.now(timezone.utc) + expires_delta
# #         if expires_delta
# #         else datetime.now(timezone.utc) + timedelta(minutes=15)
# #     )
# #     to_encode.update({"exp": expire})
# #     return jwt.encode(to_encode, secret_key, algorithm)
# #
# #
# # def create_refresh_token(data: dict, expires_delta: timedelta = None) -> str:
# #     to_encode = data.copy()
# #     expire = (
# #         datetime.now(timezone.utc) + expires_delta
# #         if expires_delta
# #         else datetime.now(timezone.utc) + timedelta(days=7)
# #     )
# #     to_encode.update({"exp": expire})
# #     return jwt.encode(to_encode, secret_key, algorithm)
#
#
# def get_user_from_token(request: Request):
#     token = request.cookies.get("access_token")
#     log.debug("Starting get_user_from_token")
#     try:
#         log.debug("token %s", token)
#         payload = jwt.decode(token, secret_key, algorithms=algorithm)
#         log.debug("Decoded payload: %s", payload)
#         username = payload.get("sub")
#         if username is None:
#             log.debug("username is None")
#             raise UnauthorizedError(validate=True)
#     except jwt.ExpiredSignatureError:
#         raise UnauthorizedError(refresh_token=True)
#     except jwt.InvalidTokenError:
#         raise UnauthorizedError(access_token=True)
#     return username
#
# def check_refresh_token(refresh_token: str, username: str):
#     try:
#         payload = jwt.decode(refresh_token, secret_key, algorithms=algorithm)
#     except jwt.ExpiredSignatureError:
#         raise UnauthorizedError(refresh_token=True)
#     except jwt.InvalidTokenError:
#         raise UnauthorizedError(access_token=True)
#
#     if payload.get("type") != "refresh":
#         raise UnauthorizedError(access_token=True)
#
#     if payload.get("sub") != username:
#         raise UnauthorizedError(access_token=True)

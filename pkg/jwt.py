import jwt
from .error import UnauthenticatedError
from .constant import ENTITY_STC, ENTITY_STC_BACKEND
from datetime import datetime, timezone, timedelta
import os

SECRET_KEY = os.getenv('SECRET_KEY')


def create_jwt(payload: dict, algorithm="HS512") -> str:
    """
    encode payload and return JWT token string
    @param payload: the JWT payload
    @param algorithm: defaults to HS512
    @return: JWT token string
    """
    return jwt.encode(payload, SECRET_KEY, algorithm)


def decode_jwt(token: str, algorithm="HS512") -> dict:
    """
    decode JWT token and return its payload
    @param token: the JWT token
    @param algorithm: defaults to HS512
    @return: payload object inside the token
    @raise UnauthenticatedError: will raise this error if token has expired
    """
    try:
        return jwt.decode(token, SECRET_KEY, algorithm)
    except jwt.ExpiredSignatureError:
        raise UnauthenticatedError('session expired')


def generate_payload(username: str) -> dict:
    """
    @param username: string
    @return:
    """
    return {
        'username': username,
        'aud': ENTITY_STC_BACKEND,
        'iss': ENTITY_STC,
        'sub': ENTITY_STC,
        'exp': datetime.now(tz=timezone.utc) + timedelta(minutes=30)
    }

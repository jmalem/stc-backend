import jwt
from utils.error import UnauthenticatedError
from utils.jwt.constant import ENTITY_STC, ENTITY_STC_BACKEND
from datetime import datetime, timezone, timedelta
import os
from flask import request
from functools import wraps

SECRET_KEY = os.getenv('SECRET_KEY')
AUTH_ENABLED = os.getenv('AUTH_ENABLED')

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
        return jwt.decode(token, SECRET_KEY, algorithm, audience=ENTITY_STC_BACKEND)
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
        'iat': datetime.now(tz=timezone.utc),
        'sub': ENTITY_STC,
        'exp': datetime.now(tz=timezone.utc) + timedelta(minutes=30)
    }


def token_required(f):
    """
    Wrapper function to authenticate user
    we have to pass user_repo as part of the services that we want to authenticate
    @param f:
    @return:
    """

    @wraps(f)
    def decorated(*args, **kwargs):
        if AUTH_ENABLED != "1":
            return f(*args)
        token = None
        if "Authorization" in request.headers:
            token = request.headers["Authorization"].split(" ")[1]
        if not token:
            return {
                       "message": "Authentication Token is missing!",
                       "data": None,
                       "error": "Unauthorized"
                   }, 401
        try:
            data = decode_jwt(token)
            username = data["username"]
            # args[0] here is equivalent to self
            current_user = args[0].user_repo.get(username)
            if current_user is None:
                return {
                           "message": "Invalid Authentication token!",
                           "data": None,
                           "error": "Unauthorized"
                       }, 401
        except Exception as e:
            return {
                       "message": "Unauthenticated",
                       "data": None,
                       "error": str(e)
                   }, 401

        return f(*args, **kwargs)

    return decorated

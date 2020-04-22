import logging
from typing import List

from redis import WatchError
from redis.client import Pipeline

from src.app.models.request.auth.oauth_request import AuthTokenRequest
from src.app.models.response.auth_token.oauth_response import AuthTokenResponse

logger = logging.getLogger('gunicorn.error')


def persist_token(redis_connection, client_id: str, client_db: int, auth_code_db: int,
                  oauth_response: AuthTokenResponse, auth_code: str):
    access_token_key = "%s:%s" % (client_id, 'access_token')
    refresh_token_key = "%s:%s" % (client_id, 'refresh_token')

    save_auth_refresh_token(redis_connection=redis_connection,
                            access_token_key=access_token_key, refresh_token_key=refresh_token_key,
                            auth_code=auth_code, oauth_response=oauth_response,
                            auth_code_db=auth_code_db, client_db=client_db)


def save_auth_refresh_token(redis_connection,
                            access_token_key, refresh_token_key,
                            auth_code, oauth_response,
                            auth_code_db, client_db, ):
    with redis_connection.pipeline() as pipe:
        redis_sadd_pipeline(pipe, access_token_key, client_db,
                            oauth_response.access_token)
        redis_sadd_pipeline(pipe, refresh_token_key, client_db,
                            oauth_response.refresh_token)

        redis_set_query_pipe(pipe=pipe, name=oauth_response.access_token, value='VALID', expire=3600,
                             db=client_db)
        redis_set_query_pipe(pipe=pipe, name=oauth_response.refresh_token, value='VALID', expire=36000,
                             db=client_db)

        redis_remove_query_pipeline(pipe=pipe, name=auth_code, db=auth_code_db)

        pipe.execute()


def redis_sadd_pipeline(pipe, name, db: int, *value):
    try:
        pipe.execute_command('SELECT', db)
        pipe.sadd(name, *value)
    except WatchError:
        logger.error(exc_info=True)


def redis_set_query_pipe(pipe: Pipeline, name: str, value: str, expire: int, db: int) -> List:
    try:
        pipe.execute_command('SELECT', db)
        pipe.set(name=name, value=value, ex=expire)
    except WatchError:
        logger.error(exc_info=True)


def redis_hmset_query_pipeline(redis_connection, name, db: int, *keys) -> List:
    with redis_connection.pipeline() as pipe:
        try:
            pipe.execute_command('SELECT', db)
            pipe.hmset(name, *keys)
            pipe_response = pipe.execute()
            return pipe_response
        except WatchError:
            logger.error(exc_info=True)


def redis_get_client_info(redis_connection, name, db: int, *keys) -> List:
    with redis_connection.pipeline() as pipe:
        try:
            pipe.execute_command('SELECT', db)
            pipe.hmget(name, *keys)
            pipe_response = pipe.execute()
            return pipe_response
        except WatchError:
            logger.error(exc_info=True)


def fetch_auth_code_client_info(redis_connection, oauth_token_request: AuthTokenRequest,
                                db_1: int,
                                db_2: int):
    with redis_connection.pipeline() as pipe:
        try:
            pipe.execute_command('SELECT', db_1)
            pipe.get(oauth_token_request.code)
            pipe.execute_command('SELECT', db_2)
            pipe.hmget(oauth_token_request.client_id, 'client_secret',
                       'redirect_uri')
            return pipe.execute()
        except WatchError:
            logger.error(exc_info=True)


def persist_auth_code(redis_connection, name: str, value: str, expire: int, db: int) -> List:
    with redis_connection.pipeline() as pipe:
        try:
            pipe.execute_command('SELECT', db)
            pipe.set(name=name, value=value, ex=expire)
            pipe_response = pipe.execute()
            return pipe_response
        except WatchError:
            logger.error(exc_info=True)


def redis_remove_query_pipeline(pipe, name, db):
    try:
        pipe.execute_command('SELECT', db)
        pipe.delete(name)
    except WatchError as we:
        logger.error(exc_info=True)

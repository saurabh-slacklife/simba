from enum import Enum


class BaseConfig:
    CONFIG_FILE_PATH = "CONFIG_FILE_PATH"
    APPLICATION_ROOT = "/v1/api"
    MAX_CONTENT_LENGTH = 1024
    LOG_LEVEL = "info"
    ENV = 'dev'
    PORT = 5000
    USER_DB = 0
    CLIENT_DB = 5
    AUTH_CODE_DB = 6
    REDIS_SOCKET_CONNECT_TIMEOUT = 30
    REDIS_SOCKET_TIMEOUT = 30
    REDIS_HEALTH_CHECK_INTERVAL = 120
    REDIS_SOCKET_KEEP_ALIVE = True
    REDIS_RETRY_ON_TIMEOUT = True
    REDIS_MAX_CONNECTION = 30
    REDIS_CONNECTION_TIMEOUT = 10
    REDIS_CLIENT_NAME = 'Simba'
    ELASTICSEARCH_CONNECTIONS = 10
    ELASTICSEARCH_DEAD_TIMEOUT = 60
    ELASTICSEARCH_TIMEOUT_CUTOFF = 5
    ELASTICSEARCH_PER_REQUEST_TIMEOUT = 5
    ELASTICSEARCH_SNIFFER_TIMEOUT = 60
    ELASTICSEARCH_TIMEOUT = 10


class ProdConfig(BaseConfig):
    LOG_LEVEL = "error"
    ENV = "prod"
    REDIS_SOCKET_CONNECT_TIMEOUT = 30
    REDIS_SOCKET_TIMEOUT = 30
    REDIS_HEALTH_CHECK_INTERVAL = 120
    REDIS_SOCKET_KEEP_ALIVE = True
    REDIS_RETRY_ON_TIMEOUT = True
    REDIS_MAX_CONNECTION = 10
    ELASTICSEARCH_CONNECTIONS = 10
    ELASTICSEARCH_DEAD_TIMEOUT = 60
    ELASTICSEARCH_TIMEOUT_CUTOFF = 5
    ELASTICSEARCH_PER_REQUEST_TIMEOUT = 5
    ELASTICSEARCH_SNIFFER_TIMEOUT = 60
    ELASTICSEARCH_TIMEOUT = 10


class StageConfig(BaseConfig):
    LOG_LEVEL = "error"
    ENV = "stage"
    REDIS_SOCKET_CONNECT_TIMEOUT = 30
    REDIS_SOCKET_TIMEOUT = 30
    REDIS_HEALTH_CHECK_INTERVAL = 120
    REDIS_SOCKET_KEEP_ALIVE = True
    REDIS_RETRY_ON_TIMEOUT = True
    REDIS_MAX_CONNECTION = 10
    ELASTICSEARCH_CONNECTIONS = 10
    ELASTICSEARCH_DEAD_TIMEOUT = 60
    ELASTICSEARCH_TIMEOUT_CUTOFF = 5
    ELASTICSEARCH_PER_REQUEST_TIMEOUT = 5
    ELASTICSEARCH_SNIFFER_TIMEOUT = 60
    ELASTICSEARCH_TIMEOUT = 10


class TestConfig(BaseConfig):
    LOG_LEVEL = "debug"
    ENV = "test"


class ConfigType(BaseConfig, Enum):
    BaseConfig = 'dev'
    ProdConfig = 'prod'
    StageConfig = 'stage'
    TestConfig = 'test'
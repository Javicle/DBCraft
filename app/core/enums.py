from enum import Enum


class ConnectionType(Enum):
    SQLITE = "sqlite"
    POSTRESQL = "postgresql"
    MYSQL = "mysql"

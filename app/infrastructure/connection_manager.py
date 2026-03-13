from sqlalchemy import create_engine, Engine
from app.infrastructure.models.system_models import ConnectionType
from app.infrastructure.crypto import decrypt_connection_string

_project_engines: dict[int, Engine] = {}


def get_project_engine(project: Project) -> Engine:
    """
    Получить Engine для проекта (Local или External).
    """
    if project.id in _project_engines:
        return _project_engines[project.id]

    if project.connection_type == ConnectionType.SQLITE:
        # Локальная БД на хостинге
        engine = create_engine(
            f"sqlite:///{project.local_db_path}",
            pool_pre_ping=True,
        )

    elif project.connection_type == ConnectionType.POSTGRESQL:
        # Внешняя PostgreSQL
        conn_string = decrypt_connection_string(project.connection_string_encrypted)
        engine = create_engine(
            conn_string,
            pool_pre_ping=True,
            pool_size=5,
            max_overflow=10,
        )

    elif project.connection_type == ConnectionType.MYSQL:
        # Внешняя MySQL
        conn_string = decrypt_connection_string(project.connection_string_encrypted)
        engine = create_engine(
            conn_string,
            pool_pre_ping=True,
        )

    else:
        raise ValueError(f"Unknown connection type: {project.connection_type}")

    _project_engines[project.id] = engine
    return engine


def test_connection(conn_string: str, db_type: str) -> bool:
    """
    Проверить подключение перед сохранением (UI валидация).
    """
    try:
        engine = create_engine(conn_string)
        with engine.connect() as conn:
            conn.execute("SELECT 1")
        return True
    except Exception:
        return False

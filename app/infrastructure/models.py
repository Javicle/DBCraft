from datetime import datetime

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import DeclarativeBase, relationship

from app.core.enums import ConnectionType


class Base(DeclarativeBase): ...


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    username = Column(String(50), unique=True, nullable=False)
    email = Column(String(120), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.now)


class Project(Base):
    __tablename__ = "projects"
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    connection_type = Column(Enum(ConnectionType), default=ConnectionType.SQLITE)
    local_db_path = Column(String(255), nullable=True)
    connection_string_encrypted = Column(Text, nullable=True)

    is_published = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.now)


# === МЕТАДАННЫЕ ПРОЕКТА (Лежат в System DB) ===


class SystemTable(Base):
    """Метаданные о таблицах пользователя"""

    __tablename__ = "system_tables"

    id = Column(Integer, primary_key=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False, index=True)
    table_name = Column(String(100), nullable=False)
    created_at = Column(DateTime, default=datetime.now)

    # Уникальность имени таблицы в рамках проекта
    __table_args__ = (
        UniqueConstraint("project_id", "table_name", name="uq_project_table"),
    )


class SystemRelation(Base):
    """Метаданные о связях (для ER-диаграммы)"""

    __tablename__ = "system_relations"

    id = Column(Integer, primary_key=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False, index=True)
    from_table = Column(String(100), nullable=False)
    from_column = Column(String(100), nullable=False)
    to_table = Column(String(100), nullable=False)
    to_column = Column(String(100), nullable=False)
    relation_type = Column(String(20), nullable=False)  # 1:1, 1:N, N:1, M:N
    constraint_name = Column(String(100), nullable=True)
    created_at = Column(DateTime, default=datetime.now)


class ProjectMember(Base):
    __tablename__ = "project_members"
    id = Column(Integer, primary_key=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    role = Column(String(20), nullable=False, default="viewer")
    __table_args__ = (UniqueConstraint("project_id", "user_id"),)


class AuditLog(Base):
    __tablename__ = "audit_log"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=True)
    action = Column(String(50), nullable=False)
    details = Column(Text, nullable=True)
    timestamp = Column(DateTime, default=datetime.now)

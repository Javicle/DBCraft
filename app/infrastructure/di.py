from sqlalchemy import Engine, create_engine

from app.domain.service import RelationService, TableService
from app.infrastructure.models import Base
from app.infrastructure.repositories import RelationRepository, SQLAlchemyRepository

from app.core.config import settings


def _create_engine() -> Engine:
    return create_engine(settings.DATABASE_URL, pool_pre_ping=True)


def _create_system_engine() -> Engine:
    return create_engine(settings.SYSTEM_DATABASE_URL, pool_pre_ping=True)


def create_services() -> dict[str, TableService | RelationService | Engine]:
    engine = _create_engine()
    Base.metadata.create_all(engine)

    table_repo = SQLAlchemyRepository(engine, Base.metadata)
    relation_repo = RelationRepository(engine, Base.metadata)

    table_service = TableService(table_repo)
    relation_service = RelationService(relation_repo, table_service)

    return {
        "table_service": table_service,
        "relation_service": relation_service,
        "engine": engine,
    }


def create_system_services() -> dict[str, TableService | RelationService | Engine]:
    engine = _create_system_engine()
    Base.metadata.create_all(engine)

    table_repo = SQLAlchemyRepository(engine, Base.metadata)
    relation_repo = RelationRepository(engine, Base.metadata)

    table_service = TableService(table_repo)
    relation_service = RelationService(relation_repo, table_service)

    return {
        "table_service": table_service,
        "relation_service": relation_service,
        "engine": engine,
    }

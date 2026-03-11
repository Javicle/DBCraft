from sqlalchemy import Engine, create_engine

from app.domain.entities import ColumnSchema, TableSchema, Relation
from app.domain.service import RelationService, TableService
from app.infrastructure.models import Base
from app.infrastructure.repositories import RelationRepository, SQLAlchemyRepository

DATABASE_URL = "sqlite:///dbcraft.db"


def _create_engine() -> Engine:
    return create_engine(DATABASE_URL, pool_pre_ping=True)


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

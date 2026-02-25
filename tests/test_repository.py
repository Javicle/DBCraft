import pytest
from sqlalchemy import MetaData, create_engine, inspect

from app.core.exceptions import TableAlreadyExistsError
from app.domain.entities import ColumnSchema, TableSchema
from app.infrastructure.repositories import SQLAlchemyRepository


@pytest.fixture
def repository() -> SQLAlchemyRepository:
    engine = create_engine("sqlite:///:memory:")
    metadata = MetaData()
    return SQLAlchemyRepository(engine, metadata)


@pytest.fixture
def schema() -> TableSchema:
    return TableSchema(
        name="users",
        columns=[
            ColumnSchema(
                name="id", column_type="INT", primary_key=True, nullable=False
            ),
            ColumnSchema(
                name="name", column_type="VARCHAR", nullable=True, primary_key=False
            ),
        ],
    )


def test_create_table(repository: SQLAlchemyRepository, schema: TableSchema):
    repository.create_table(schema)
    inspector = inspect(repository.engine)
    assert inspector.has_table("users")

    columns = inspector.get_columns("users")

    assert columns[0]["name"] == "id"
    assert columns[0]["nullable"] == False

    assert columns[1]["name"] == "name"
    assert columns[1]["nullable"] == True
    pk = inspector.get_pk_constraint("users")
    assert "id" in pk["constrained_columns"]
    assert "INT" in str(columns[0]["type"]).upper()  # INTEGER
    assert "CHAR" in str(columns[1]["type"]).upper()  # VARCHAR


def test_delete_table(repository: SQLAlchemyRepository, schema: TableSchema) -> None:
    repository.create_table(schema)
    inspector = inspect(repository.engine)
    assert inspector.has_table("users")
    repository.delete_table(schema.name)
    assert not inspect(repository.engine).has_table(table_name="users")


def test_all_table(repository: SQLAlchemyRepository, schema: TableSchema) -> None:
    repository.create_table(schema)
    tables = repository.get_all_tables()

    created_table = next((t for t in tables if t.name == schema.name), None)

    assert created_table is not None
    assert len(created_table.columns) == len(schema.columns)
    assert created_table.columns[0].name == "id"


def test_create_duplicate_table(repository: SQLAlchemyRepository, schema: TableSchema):
    repository.create_table(schema)
    with pytest.raises(TableAlreadyExistsError):
        repository.create_table(schema)

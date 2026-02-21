import pytest
from sqlalchemy import MetaData, create_engine, inspect

from app.domain.entities import ColumnSchema, TableSchema
from app.infrastructure.repositories import SQLAlchemyRepository


@pytest.fixture()
def repository() -> SQLAlchemyRepository:
    engine = create_engine("sqlite:///:memory:")
    metadata = MetaData()
    return SQLAlchemyRepository(engine, metadata)


def test_create_table(repository: SQLAlchemyRepository):
    schema = TableSchema(
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
    repository.create_table(schema)
    inspector = inspect(repository.engine)
    assert inspector.has_table("users")

    columns = inspector.get_columns("users")

    assert columns[0]["name"] == "id"
    assert (
        columns[0]["primary_key"] == True
    )  # pyright : ignore[reportGeneralTypeIssues]
    assert columns[0]["nullable"] == False

    assert columns[1]["name"] == "name"
    assert columns[1]["nullable"] == True
    assert columns[1]["primary_key"] == False

    assert "INT" in str(columns[0]["type"]).upper()  # INTEGER
    assert "CHAR" in str(columns[1]["type"]).upper()  # VARCHAR

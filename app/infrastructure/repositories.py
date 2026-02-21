from sqlalchemy import (
    Boolean,
    Column,
    Engine,
    Float,
    Integer,
    MetaData,
    String,
    Table,
    inspect,
)
from typing_extensions import override

from app.domain.entities import ColumnSchema, TableSchema
from app.domain.repositories import BaseTableRepository

column_type_dict = {
    "INT": Integer(),
    "VARCHAR": String(255),
    "BOOLEAN": Boolean(),
    "FLOAT": Float(),
}
SQLA_TO_DOMAIN = {
    Integer: "INT",
    String: "VARCHAR",
    Boolean: "BOOLEAN",
    Float: "FLOAT",
}


class SQLAlchemyRepository(BaseTableRepository):
    def __init__(self, engine: Engine, metadata: MetaData) -> None:
        self.engine = engine
        self.metadata = metadata

    @override
    def create_table(self, schema: TableSchema) -> None:
        columns = [
            Column(
                name=column.name,
                type_=column_type_dict[column.column_type],  # pyright: ignore[reportArgumentType]
                primary_key=column.primary_key,
                nullable=column.nullable,
            )
            for column in schema.columns
        ]

        table = Table(schema.name, self.metadata, *columns)
        table.create(self.engine)

    @override
    def delete_table(self, schema: TableSchema) -> None:
        insp = inspect(self.engine)
        if insp.has_table(schema.name):
            table = Table(schema.name, self.metadata, autoload_with=self.engine)
            table.drop(self.engine)

    @override
    def get_all_tables(self) -> list[TableSchema]:
        insp = inspect(self.engine)
        results: list[TableSchema] = []

        for name in insp.get_table_names():
            table = Table(name, self.metadata, autoload_with=self.engine)
            columns_list = [
                ColumnSchema(
                    name=col.name,
                    column_type=SQLA_TO_DOMAIN.get(type(col.type), "VARCHAR"),  # pyright: ignore[reportArgumentType]
                    nullable=True if col.nullable else False,
                    primary_key=col.primary_key,
                )
                for col in table.columns
            ]
            results.append(TableSchema(name=name, columns=columns_list))

        return results

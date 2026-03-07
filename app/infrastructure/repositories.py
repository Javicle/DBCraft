from sqlalchemy import (
    Boolean,
    Column,
    Engine,
    Float,
    ForeignKey,
    Integer,
    MetaData,
    String,
    Table,
    inspect,
    text,
)
from typing_extensions import override

from app.core.exceptions import TableAlreadyExistsError, TableNotExistsError
from app.domain.entities import ColumnSchema, Relation, TableSchema
from app.domain.repositories import BaseRelationRepository, BaseTableRepository

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
        inspector = inspect(self.engine)
        if inspector.has_table(schema.name):
            raise TableAlreadyExistsError(
                f"Table with name: {schema.name} already exists"
            )
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
    def delete_table(self, name: str) -> None:
        insp = inspect(self.engine)
        if insp.has_table(name):
            table = Table(name, self.metadata, autoload_with=self.engine)
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
                    column_type=SQLA_TO_DOMAIN.get(type(col.type), "VARCHAR"),  # pyright: ignore[]
                    nullable=True if col.nullable else False,
                    primary_key=col.primary_key,
                )
                for col in table.columns
            ]
            results.append(TableSchema(name=name, columns=columns_list))

        return results

    @override
    def get_table(self, name: str) -> Table:
        table = self.metadata.tables.get(name)
        if table is None:
            raise TableNotExistsError(f"Table with name: {name} not exists")
        return table


class RelationRepository(BaseRelationRepository):
    def __init__(self, engine: Engine, metadata: MetaData) -> None:
        self.engine = engine
        self.metadata = metadata

    @override
    def add_relation(self, relation: Relation) -> None:
        insp = inspect(self.engine)
        if not insp.has_table(relation.from_table):
            raise TableNotExistsError(
                f"From Table with name: {relation.from_table} not exists"
            )
        if not insp.has_table(relation.to_table):
            raise TableNotExistsError(
                f"To Table with name: {relation.to_table} not exists"
            )
        if relation.relation_type in ("1:1" or "N:1"):
            constraint_name = f"fk_{relation.from_table}_{relation.from_column}"
            sql = text(f"""
                ALTER TABLE {relation.from_table}
                ADD COLUMN {relation.from_column}
                ADD constraint_name {constraint_name}
                FOREIGH KEY ({relation.from_column})
                REFERENCES {relation.to_table}({relation.to_column})
            """)
            with self.engine.connect() as conn:
                conn.execute(sql)
                conn.commit()

        elif relation.relation_type == "M:N":
            junction_name = f"{relation.from_table}_{relation.to_table}_rel"
            if not insp.has_table(junction_name):
                junction = Table(
                    junction_name,
                    self.metadata,
                    Column(
                        relation.from_table,
                        Integer,
                        ForeignKey(f"{relation.from_table}.{relation.from_column}"),
                        primary_key=True,
                    ),
                    Column(
                        relation.to_table,
                        Integer,
                        ForeignKey(f"{relation.to_table}.{relation.to_column}"),
                        primary_key=True,
                    ),
                )
                junction.create(self.engine)

        system_sql = text("""
                INSERT INTO system_relations (from_table, from_column, to_table, to_column, relation_type)
                VALUES (:from_table, :from_column, :to_table, :to_column, :relation_type)
            """)
        with self.engine.connect() as conn:
            conn.execute(
                system_sql,
                {
                    "from_table": relation.from_table,
                    "from_column": relation.from_column,
                    "to_table": relation.to_table,
                    "to_column": relation.to_column,
                    "relation_type": relation.relation_type,
                },
            )
            conn.commit()

    @override
    def delete_relation(self, relation_id: int) -> None:
        with self.engine.connect() as conn:
            res = conn.execute(
                text(
                    "SELECT constraint_name, from_table FROM system_relations WHERE id =:id"
                ),
                {"id": relation_id},
            )

            if not res:
                ValueError("Relation not found")

            constraint_name, from_table = res

            if constraint_name:
                conn.execute(
                    text(
                        f"ALTER TABLE {from_table} DROP CONSTRAINT IF EXISTS {constraint_name}"
                    )
                )

            conn.execute(
                text("DELETE FROM system_relations WHERE id = :id"), {"id": relation_id}
            )
            conn.commit

    @override
    def get_all_relations(self) -> list[Relation]:
        with self.engine.connect() as conn:
            rows = conn.execute(text("SELECT * FROM system_relations")).fetchall()

        return [
            Relation(
                id=r.id,
                from_table=r.from_table,
                from_column=r.from_column,
                to_table=r.to_table,
                to_column=r.to_column,
                relation_type=r.relation_type,
            )
            for r in rows
        ]

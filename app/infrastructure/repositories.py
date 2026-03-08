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
            raise TableNotExistsError(f"Table '{relation.from_table}' not exists")
        if not insp.has_table(relation.to_table):
            raise TableNotExistsError(f"Table '{relation.to_table}' not exists")

        with self.engine.begin() as conn:
            constraint_name = None

            if relation.relation_type in ("N:1", "1:1"):
                constraint_name = f"fk_{relation.from_table}_{relation.from_column}"
                sql = text(f"""
                    ALTER TABLE {relation.from_table}
                    ADD CONSTRAINT {constraint_name}
                    FOREIGN KEY ({relation.from_column})
                    REFERENCES {relation.to_table}({relation.to_column})
                """)
                conn.execute(sql)

            elif relation.relation_type == "1:N":
                constraint_name = f"fk_{relation.to_table}_{relation.to_column}"
                sql = text(f"""
                    ALTER TABLE {relation.to_table}
                    ADD CONSTRAINT {constraint_name}
                    FOREIGN KEY ({relation.to_column})
                    REFERENCES {relation.from_table}({relation.from_column})
                """)
                conn.execute(sql)

            elif relation.relation_type == "M:N":
                junction_name = f"{relation.from_table}_{relation.to_table}_rel"
                constraint_name = (
                    junction_name  # Сохраним имя таблицы вместо имени констрейнта
                )

                if not insp.has_table(junction_name):
                    # В идеале здесь нужно динамически узнавать тип PK (Integer, String, UUID)
                    junction = Table(
                        junction_name,
                        self.metadata,
                        Column(
                            f"{relation.from_table}_id",
                            Integer,
                            ForeignKey(f"{relation.from_table}.{relation.from_column}"),
                            primary_key=True,
                        ),
                        Column(
                            f"{relation.to_table}_id",
                            Integer,
                            ForeignKey(f"{relation.to_table}.{relation.to_column}"),
                            primary_key=True,
                        ),
                    )
                    # Выполняем создание таблицы через текущее соединение
                    junction.create(conn)

            # Запись в системную таблицу в той же транзакции
            system_sql = text("""
                INSERT INTO system_relations 
                (from_table, from_column, to_table, to_column, relation_type, constraint_name)
                VALUES (:from_table, :from_column, :to_table, :to_column, :relation_type, :constraint_name)
            """)
            conn.execute(
                system_sql,
                {
                    "from_table": relation.from_table,
                    "from_column": relation.from_column,
                    "to_table": relation.to_table,
                    "to_column": relation.to_column,
                    "relation_type": relation.relation_type,
                    "constraint_name": constraint_name,
                },
            )

    @override
    def delete_relation(self, relation_id: int) -> None:
        db_dialect = (
            self.engine.dialect.name
        )  # Вернет 'sqlite', 'postgresql', 'mysql' и т.д.

        with self.engine.begin() as conn:
            # Используем .mappings(), чтобы обращаться к результату как к словарю
            res = (
                conn.execute(
                    text("""
                    SELECT constraint_name, from_table, to_table, relation_type 
                    FROM system_relations 
                    WHERE id = :id
                """),
                    {"id": relation_id},
                )
                .mappings()
                .fetchone()
            )

            if not res:
                raise ValueError(f"Relation with id {relation_id} not found")

            constraint_name = res["constraint_name"]
            from_table = res["from_table"]
            to_table = res["to_table"]
            relation_type = res["relation_type"]
            if constraint_name:
                if relation_type == "M:N":
                    conn.execute(text(f"DROP TABLE IF EXISTS {constraint_name}"))
                else:
                    table_name = to_table if relation_type == "1:N" else from_table

                    # Ветвим логику в зависимости от базы данных
                    if db_dialect == "sqlite":
                        # В SQLite нельзя просто сделать DROP CONSTRAINT.
                        # Здесь мы либо используем обходной путь (Alembic Batch),
                        # либо (если это пет-проект/тесты) просто пропускаем удаление FK на уровне БД,
                        # удаляя связь только из нашей системной таблицы system_relations.
                        print(
                            f"Warning: SQLite doesn't support DROP CONSTRAINT. Skipping schema alter for {table_name}."
                        )
                    else:
                        # Для нормальных БД (PG, MySQL) всё работает как часы
                        conn.execute(
                            text(
                                f"ALTER TABLE {table_name} DROP CONSTRAINT IF EXISTS {constraint_name}"
                            )
                        )

            # Удаляем запись из системной таблицы (работает везде)
            conn.execute(
                text("DELETE FROM system_relations WHERE id = :id"), {"id": relation_id}
            )

from typing import Literal

from pydantic import BaseModel, Field

ColumnType = Literal["INT", "VARCHAR", "DATE", "FLOAT", "BOOLEAN"]


class ColumnSchema(BaseModel):
    primary_key: bool = Field(False)
    name: str
    nullable: bool = Field(default=False)
    column_type: ColumnType


class TableSchema(BaseModel):
    name: str
    columns: list[ColumnSchema]


RelationTypes = Literal["1:1"] | Literal["M:N"] | Literal["N:1"] | Literal["Self"]


class Relation(BaseModel):
    id: int
    from_table: str
    from_column: str
    to_table: str
    to_column: str
    relation_type: RelationTypes

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

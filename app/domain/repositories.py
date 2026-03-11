from abc import ABC, abstractmethod

from sqlalchemy import Table

from app.domain.entities import Relation, TableSchema


class BaseTableRepository(ABC):
    @abstractmethod
    def create_table(self, schema: TableSchema) -> None: ...

    @abstractmethod
    def delete_table(self, name: str) -> None: ...

    @abstractmethod
    def get_all_tables(self) -> list[TableSchema]: ...

    @abstractmethod
    def get_table(self, name: str) -> Table: ...


class BaseRelationRepository(ABC):
    @abstractmethod
    def add_relation(self, relation: Relation) -> None: ...

    @abstractmethod
    def delete_relation(self, relation_id: int) -> None: ...

    @abstractmethod
    def get_all_relations(self) -> list[Relation]: ...

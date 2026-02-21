from abc import ABC, abstractmethod

from app.domain.entities import TableSchema


class BaseTableRepository(ABC):
    @abstractmethod
    def create_table(self, schema: TableSchema) -> None: ...

    @abstractmethod
    def delete_table(self, schema: TableSchema) -> None: ...

    @abstractmethod
    def get_all_tables(self) -> list[TableSchema]: ...

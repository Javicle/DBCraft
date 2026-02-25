from app.core.exceptions import TableAlreadyExistsError
from app.domain.entities import TableSchema
from app.domain.repositories import BaseTableRepository


class TableService:
    def __init__(self, repo: BaseTableRepository) -> None:
        self.repo = repo

    def create_table(self, schema: TableSchema):
        try:
            self.repo.create_table(schema=schema)
        except TableAlreadyExistsError as exc:
            raise exc

    def delete_table(self, name: str):
        self.repo.delete_table(name)

    def get_all_tables(self) -> list[TableSchema]:
        return self.repo.get_all_tables()

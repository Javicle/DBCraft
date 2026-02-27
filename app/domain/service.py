from app.core.exceptions import TableAlreadyExistsError
from app.domain.entities import Relation, TableSchema
from app.domain.repositories import BaseRelationRepository, BaseTableRepository


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


class RelationService:
    def __init__(
        self, repo: BaseRelationRepository, table_service: TableService
    ) -> None:
        self.repo = repo
        self.table_service = table_service

    def add_relation(self, relation: Relation) -> None:
        # Валидация: существуют ли таблицы
        self.repo.add_relation(relation)

    def get_all_relations(self) -> list[Relation]:
        return self.repo.get_all_relations()

    def delete_relation(self, relation_id: int) -> None:
        self.repo.delete_relation(relation_id)

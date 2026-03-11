from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase): ...


class SystemRelation(Base):
    __tablename__ = "system_relations"

    id = Column(Integer, primary_key=True, autoincrement=True)
    from_table = Column(String, nullable=False)
    from_column = Column(String, nullable=False)
    to_table = Column(String, nullable=False)
    to_column = Column(String, nullable=False)
    relation_type = Column(String, nullable=False)
    constraint_name = Column(String, nullable=True)

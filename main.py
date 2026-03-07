import numpy as np
import pandas as pd
import streamlit as st
from sqlalchemy import MetaData, create_engine

from app.domain.entities import ColumnSchema, TableSchema
from app.domain.service import RelationService, TableService
from app.infrastructure.repositories import RelationRepository, SQLAlchemyRepository
from app.ui.pyvis_test import render_db_schema


class MainLauncher:
    def __init__(
        self, table_service: TableService, relations_service: RelationService
    ) -> None:
        self.table_service = table_service
        self.relations_service = relations_service

    def launch_page(self) -> None:
        # 1. Заголовок и текст
        st.title("Моё первое приложение 🚀")
        st.write("Streamlit превращает скрипты в веб-интерфейсы за считанные минуты.")

        # 2. Интерактивные виджеты (ввод данных)
        name = st.text_input("Как тебя зовут?", "Аноним")
        age = st.slider("Выбери свой возраст", 0, 100, 25)

        if st.button("Поприветствовать"):
            st.success(f"Привет, {name}! Тебе {age} лет.")

        # 3. Работа с данными и графиками
        st.subheader("Визуализация случайных чисел")
        chart_data = pd.DataFrame(np.random.randn(20, 3), columns=["a", "b", "c"])

        # Отображаем таблицу (можно сворачивать)
        with st.expander("Посмотреть сырые данные"):
            st.dataframe(chart_data)

        # Рисуем график
        st.line_chart(chart_data)

        # 4. Боковая панель (Sidebar)
        st.sidebar.header("Настройки")
        st.sidebar.checkbox("Показать секретное сообщение")

        st.subheader("Схема БД")
        render_db_schema(
            self.table_service.get_all_tables(),
            self.relations_service.get_all_relations(),
        )


engine = create_engine("sqlite:///:memory:")
metadata = MetaData()

sqlalchemy_repository = SQLAlchemyRepository(engine, metadata)
relation_repository = RelationRepository(engine, metadata)

table_service = TableService(sqlalchemy_repository)
relation_service = RelationService(relation_repository, table_service)
starter = MainLauncher(table_service, relation_service)


schema = TableSchema(
    name="users",
    columns=[
        ColumnSchema(name="id", column_type="INT", primary_key=True, nullable=False),
        ColumnSchema(
            name="name", column_type="VARCHAR", nullable=True, primary_key=False
        ),
    ],
)


table_service.create_table(schema)

starter.launch_page()

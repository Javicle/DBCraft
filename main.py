import numpy as np
import pandas as pd
import streamlit as st
from sqlalchemy import create_engine

from app.domain.entities import ColumnSchema, TableSchema, Relation
from app.domain.service import RelationService, TableService
from app.infrastructure.models import Base
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
metadata = Base.metadata

sqlalchemy_repository = SQLAlchemyRepository(engine, metadata)
relation_repository = RelationRepository(engine, metadata)

table_service = TableService(sqlalchemy_repository)
relation_service = RelationService(relation_repository, table_service)
starter = MainLauncher(table_service, relation_service)

schema_users = TableSchema(
    name="users",
    columns=[
        ColumnSchema(name="id", column_type="INT", primary_key=True, nullable=False),
        ColumnSchema(
            name="name", column_type="VARCHAR", nullable=True, primary_key=False
        ),
        ColumnSchema(
            name="email", column_type="VARCHAR", nullable=False, primary_key=False
        ),
    ],
)

# 2. Orders
schema_orders = TableSchema(
    name="orders",
    columns=[
        ColumnSchema(name="id", column_type="INT", primary_key=True, nullable=False),
        ColumnSchema(
            name="user_id", column_type="INT", nullable=False, primary_key=False
        ),
        ColumnSchema(
            name="total", column_type="FLOAT", nullable=True, primary_key=False
        ),
        ColumnSchema(
            name="created_at", column_type="DATE", nullable=True, primary_key=False
        ),
    ],
)

# 3. Products
schema_products = TableSchema(
    name="products",
    columns=[
        ColumnSchema(name="id", column_type="INT", primary_key=True, nullable=False),
        ColumnSchema(
            name="name", column_type="VARCHAR", nullable=False, primary_key=False
        ),
        ColumnSchema(
            name="price", column_type="FLOAT", nullable=False, primary_key=False
        ),
    ],
)

# 4. Order_Items
schema_order_items = TableSchema(
    name="order_items",
    columns=[
        ColumnSchema(name="id", column_type="INT", primary_key=True, nullable=False),
        ColumnSchema(
            name="order_id", column_type="INT", nullable=False, primary_key=False
        ),
        ColumnSchema(
            name="product_id", column_type="INT", nullable=False, primary_key=False
        ),
        ColumnSchema(
            name="quantity", column_type="INT", nullable=False, primary_key=False
        ),
    ],
)

# Создаём все таблицы
metadata.create_all(engine)
table_service.create_table(schema_users)
table_service.create_table(schema_orders)
table_service.create_table(schema_products)
table_service.create_table(schema_order_items)

# === Создаём связи ===

# users -> orders (1:N)
relation_service.add_relation(
    Relation(
        id=1,
        from_table="users",
        from_column="id",
        to_table="orders",
        to_column="user_id",
        relation_type="N:1",
    )
)

# orders -> order_items (1:N)
relation_service.add_relation(
    Relation(
        id=2,
        from_table="orders",
        from_column="id",
        to_table="order_items",
        to_column="order_id",
        relation_type="1:N",
    )
)

# products -> order_items (1:N)
relation_service.add_relation(
    Relation(
        id=3,
        from_table="products",
        from_column="id",
        to_table="order_items",
        to_column="product_id",
        relation_type="1:N",
    )
)


metadata.create_all(engine)

starter.launch_page()

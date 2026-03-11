import sys
from pathlib import Path

import streamlit as st
from sqlalchemy import Engine

# Настройка путей (оставляем твою логику)
ROOT_DIR = Path(__file__).resolve().parent.parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from app.domain.service import RelationService, TableService
from app.ui.deps import get_services
from app.ui.pyvis_test import render_db_schema

# Получение сервисов
services = get_services()
table_service: TableService = services["table_service"]  # type: ignore
relation_service: RelationService = services["relation_service"]  # type: ignore
engine: Engine = services["engine"]  # type: ignore

# Конфигурация страницы
st.set_page_config(
    page_title="DBCraft | Dashboard",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded",
)

# --- Кастомный CSS для красоты ---

# --- Заголовок ---
col_title, col_logo = st.columns([4, 1])
with col_title:
    st.title("🚀 DBCraft")
    st.markdown("#### Интеллектуальная система проектирования архитектуры баз данных")
with col_logo:
    # Здесь можно вывести версию или статус подключения
    st.success(f"Connected: {engine.dialect.name.upper()}")

st.divider()

# --- Сбор данных для Dashboard ---
tables = table_service.get_all_tables()
relations = relation_service.get_all_relations()
total_columns = sum(len(t.columns) for t in tables)

# --- Блок метрик (Dashboard) ---
m1, m2, m3, m4 = st.columns(4)

with m1:
    st.metric(label="Таблицы", value=len(tables), delta="Объектов в схеме")
with m2:
    st.metric(label="Связи", value=len(relations), delta="FK констрейнтов")
with m3:
    st.metric(label="Колонки", value=total_columns, delta="Всего полей")
with m4:
    # Иконка СУБД в зависимости от движка
    db_icon = "🐘" if "postgre" in engine.dialect.name.lower() else "🗄️"
    st.metric(
        label="Движок БД", value=engine.dialect.name.upper(), delta=f"{db_icon} Active"
    )

st.write("")  # Отступ


# --- Основной контент ---
tab_viz, tab_summary = st.tabs(["🗺️ ER-диаграмма", "📋 Сводка данных"])


with tab_viz:
    st.subheader("🗺️ ER-диаграмма")

    col_left, col_right = st.columns([3, 1])
    with col_right:
        # Выбор режима отображения
        viz_mode = st.radio(
            "Режим схемы:",
            ["Organic", "Structural"],
            help="Organic — можно таскать таблицы, Structural — строгая иерархия",
        )

    with col_left:
        layout_type = "Physics" if viz_mode == "Organic" else "Hierarchical"
        if tables:
            render_db_schema(tables, relations, layout_type)
        else:
            st.info("Создайте таблицы для визуализации")


with tab_summary:
    if tables:
        st.subheader("Быстрый обзор структуры")
        # Создаем DataFrame для наглядности
        summary_data = []
        for t in tables:
            pk_count = sum(1 for c in t.columns if c.primary_key)
            summary_data.append(
                {
                    "Имя таблицы": t.name,
                    "Колонок": len(t.columns),
                    "PK полей": pk_count,
                    "Типы": ", ".join(set(c.column_type for c in t.columns)),
                }
            )
        st.table(summary_data)
    else:
        st.warning("Данные отсутствуют")

# --- Нижняя панель: Быстрые действия ---
st.divider()
st.subheader("🛠️ Быстрые инструменты")
c1, c2, c3 = st.columns(3)

with c1:
    with st.container(border=True):
        st.markdown("**Новая сущность**")
        st.write("Добавить таблицу и определить её атрибуты.")
        if st.button("➕ Создать таблицу", use_container_width=True):
            st.switch_page("pages/Таблицы.py")

with c2:
    with st.container(border=True):
        st.markdown("**Управление связями**")
        st.write("Настроить Foreign Keys между таблицами.")
        if st.button("🔗 Настроить FK", use_container_width=True):
            # Поменяй путь на свой реальный файл связей
            st.switch_page("pages/Связи.py")

with c3:
    with st.container(border=True):
        st.markdown("**Экспорт и SQL**")
        st.write("Просмотреть сгенерированный SQL или экспортировать схему.")
        if st.button("📄 Посмотреть SQL", use_container_width=True):
            st.toast("Функция в разработке", icon="🚧")

# Footer
st.markdown(
    """
    <div style="text-align: center; color: grey; padding: 20px;">
        <small>DBCraft v0.1-alpha | Построено на SQLAlchemy & Streamlit</small>
    </div>
    """,
    unsafe_allow_html=True,
)

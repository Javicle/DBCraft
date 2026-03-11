import re
import streamlit as st
from app.domain.entities import ColumnSchema, TableSchema
from app.domain.service import TableService
from app.ui.deps import get_services

# Настройка страницы
st.set_page_config(page_title="Таблицы", page_icon="📋", layout="wide")

services = get_services()
table_service: TableService = services["table_service"]

# === Инициализация session_state ===
if "columns_list" not in st.session_state:
    st.session_state.columns_list = []
if "show_create_form" not in st.session_state:
    st.session_state.show_create_form = False
if "col_error" not in st.session_state:
    st.session_state.col_error = None


# === Вспомогательные функции ===
def validate_identifier(name: str) -> bool:
    """Проверка имени таблицы/колонки на SQL-инъекции и спецсимволы"""
    return bool(re.match(r"^[a-zA-Z0-9_]+$", name))


# === Коллбэки (Безопасное изменение состояния) ===


def add_column_callback():
    """Добавление колонки в список и очистка полей ввода"""
    name = st.session_state.get("new_col_name", "").strip()
    col_type = st.session_state.get("new_col_type", "INT")
    is_pk = st.session_state.get("new_col_pk", False)
    # Если это Primary Key, nullable всегда False
    is_nullable = False if is_pk else st.session_state.get("new_col_nullable", True)

    # Валидация
    if not name:
        st.session_state.col_error = "⚠️ Имя колонки не может быть пустым"
        return
    if not validate_identifier(name):
        st.session_state.col_error = "⚠️ Недопустимое имя (используйте a-z, 0-9, _)"
        return
    if any(c["name"].lower() == name.lower() for c in st.session_state.columns_list):
        st.session_state.col_error = f"⚠️ Колонка '{name}' уже добавлена"
        return

    # Успешное добавление
    st.session_state.columns_list.append(
        {"name": name, "type": col_type, "pk": is_pk, "nullable": is_nullable}
    )

    # Сброс полей ввода (ключи виджетов)
    st.session_state.new_col_name = ""
    st.session_state.new_col_pk = False
    st.session_state.new_col_nullable = True
    st.session_state.col_error = None


def delete_column_callback(index: int):
    """Удаление колонки по индексу"""
    if 0 <= index < len(st.session_state.columns_list):
        st.session_state.columns_list.pop(index)


def reset_form_callback():
    """Полный сброс формы создания"""
    st.session_state.show_create_form = False
    st.session_state.columns_list = []
    st.session_state.col_error = None
    if "table_name_input" in st.session_state:
        st.session_state.table_name_input = ""


# === UI ИНТЕРФЕЙС ===

st.title("📋 Управление таблицами")

# 1. Кнопка вызова формы
if not st.session_state.show_create_form:
    if st.button("➕ Создать новую таблицу", type="primary"):
        st.session_state.show_create_form = True
        st.rerun()

# 2. Форма создания таблицы
if st.session_state.show_create_form:
    st.subheader("Конструктор новой таблицы")

    with st.container(border=True):
        table_name = st.text_input(
            "Название таблицы", key="table_name_input", placeholder="users_data"
        )

        st.markdown("#### Список колонок")

        # Вывод уже добавленных колонок
        if not st.session_state.columns_list:
            st.info(
                "Добавьте хотя бы одну колонку (минимум один Primary Key рекомендуется)"
            )
        else:
            # Заголовки таблицы
            h1, h2, h3, h4, h5 = st.columns([3, 2, 1, 1, 1])
            h1.caption("Имя")
            h2.caption("Тип")
            h3.caption("PK")
            h4.caption("Null")
            h5.caption("Действие")

            for idx, col in enumerate(st.session_state.columns_list):
                c1, c2, c3, c4, c5 = st.columns([3, 2, 1, 1, 1])
                c1.code(col["name"])
                c2.code(col["type"])
                c3.write("🔑" if col["pk"] else "")
                c4.write("✅" if col["nullable"] else "❌")

                # Кнопка удаления с использованием коллбэка
                c5.button(
                    "🗑️", key=f"del_{idx}", on_click=delete_column_callback, args=(idx,)
                )

        st.divider()

        # Форма добавления новой колонки
        st.markdown("**Добавить новую колонку:**")
        row_c1, row_c2, row_c3, row_c4, row_c5 = st.columns([3, 2, 1, 1, 1.5])

        with row_c1:
            st.text_input("Имя", key="new_col_name", placeholder="id")
        with row_c2:
            st.selectbox(
                "Тип",
                ["INT", "BIGINT", "VARCHAR", "TEXT", "DATE", "BOOLEAN", "FLOAT"],
                key="new_col_type",
            )
        with row_c3:
            is_pk = st.checkbox("PK", key="new_col_pk")
        with row_c4:
            # Если выбран PK, чекбокс Nullable отключается
            st.checkbox("Null", key="new_col_nullable", value=not is_pk, disabled=is_pk)
        with row_c5:
            st.markdown(
                "<div style='margin-top: 1.6rem;'></div>", unsafe_allow_html=True
            )
            st.button(
                "Добавить", on_click=add_column_callback, use_container_width=True
            )

        if st.session_state.col_error:
            st.error(st.session_state.col_error)

    # Кнопки сохранения/отмены
    act_1, act_2, _ = st.columns([1, 1, 4])
    with act_1:
        if st.button("💾 Сохранить", type="primary", use_container_width=True):
            if not table_name:
                st.error("Укажите имя таблицы")
            elif not validate_identifier(table_name):
                st.error("Недопустимое имя таблицы")
            elif not st.session_state.columns_list:
                st.error("Добавьте колонки")
            elif not any(c["pk"] for c in st.session_state.columns_list):
                st.warning("Рекомендуется добавить хотя бы один Primary Key")
            else:
                try:
                    columns = [
                        ColumnSchema(
                            name=c["name"],
                            column_type=c["type"],
                            primary_key=c["pk"],
                            nullable=c["nullable"],
                        )
                        for c in st.session_state.columns_list
                    ]
                    schema = TableSchema(name=table_name, columns=columns)
                    table_service.create_table(schema)
                    st.success(f"Таблица '{table_name}' создана!")
                    reset_form_callback()
                    st.rerun()
                except Exception as e:
                    st.error(f"Ошибка: {e}")
    with act_2:
        st.button("❌ Отмена", on_click=reset_form_callback, use_container_width=True)

st.divider()

# 3. Список существующих таблиц
st.subheader("Существующие таблицы")
try:
    tables = table_service.get_all_tables()
    if not tables:
        st.info("База данных пуста.")
    else:
        for table in tables:
            with st.expander(f"🗄️ {table.name}"):
                # Формируем данные для красивого отображения
                display_data = []
                for c in table.columns:
                    display_data.append(
                        {
                            "Колонка": c.name,
                            "Тип": c.column_type,
                            "PK": "🔑" if c.primary_key else "",
                            "Nullable": "Да" if c.nullable else "Нет",
                        }
                    )
                st.table(display_data)

                # Удаление таблицы
                if st.button(f"🗑️ Удалить {table.name}", key=f"drop_{table.name}"):
                    table_service.delete_table(table.name)
                    st.rerun()
except Exception as e:
    st.error(f"Ошибка загрузки данных: {e}")

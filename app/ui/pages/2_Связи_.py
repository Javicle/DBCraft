import streamlit as st
from app.domain.entities import Relation
from app.domain.service import RelationService, TableService
from app.ui.deps import get_services

st.set_page_config(page_title="Связи", page_icon="🔗", layout="wide")

services = get_services()
table_service: TableService = services["table_service"]  # type: ignore
relation_service: RelationService = services["relation_service"]  # type: ignore

# === Session State ===
if "show_create_form" not in st.session_state:
    st.session_state.show_create_form = False
if "form_error" not in st.session_state:
    st.session_state.form_error = None


# === Коллбэки ===
def reset_form_callback():
    st.session_state.show_create_form = False
    st.session_state.form_error = None


def create_relation_callback():
    """Создание связи после валидации"""
    from_table = st.session_state.get("from_table_select")
    from_column = st.session_state.get("from_column_select")
    to_table = st.session_state.get("to_table_select")
    to_column = st.session_state.get("to_column_select")
    relation_type = st.session_state.get("relation_type_select")

    # Валидация
    if not all([from_table, from_column, to_table, to_column, relation_type]):
        st.session_state.form_error = "⚠️ Заполните все поля"
        return
    if from_table == to_table and relation_type not in ("Self", "1:1"):
        st.session_state.form_error = "⚠️ Для связи с самой собой выберите тип 'Self'"
        return
    if from_table == to_table and from_column == to_column:
        st.session_state.form_error = "⚠️ Колонки не могут совпадать"
        return

    try:
        relation = Relation(
            id=0,  # Автогенерация в БД
            from_table=from_table,
            from_column=from_column,
            to_table=to_table,
            to_column=to_column,
            relation_type=relation_type,  # type: ignore
        )
        relation_service.add_relation(relation)
        st.success(f"Связь создана: {from_table} → {to_table}")
        reset_form_callback()
        st.rerun()
    except Exception as e:
        st.session_state.form_error = f"⚠️ Ошибка: {e}"


# === UI ===
st.title("🔗 Управление связями")

# 1. Кнопка создания
if not st.session_state.show_create_form:
    if st.button("➕ Новая связь", type="primary"):
        st.session_state.show_create_form = True
        st.rerun()

# 2. Форма создания
if st.session_state.show_create_form:
    st.subheader("Конструктор связи")

    with st.container(border=True):
        tables = table_service.get_all_tables()
        if not tables:
            st.warning("Сначала создайте таблицы!")
            st.button("❌ Отмена", on_click=reset_form_callback)
            st.stop()

        # Словарь таблиц: имя → список колонок
        table_columns = {t.name: [c.name for c in t.columns] for t in tables}
        table_names = list(table_columns.keys())

        # Row 1: From
        st.markdown("**Откуда (From):**")
        r1_c1, r1_c2 = st.columns(2)
        with r1_c1:
            from_table = st.selectbox(
                "Таблица", table_names, key="from_table_select", index=0
            )
        with r1_c2:
            # Динамический список колонок выбранной таблицы
            from_cols = table_columns[from_table]
            from_column = st.selectbox(
                "Колонка", from_cols, key="from_column_select", index=0
            )

        # Row 2: Тип связи
        st.markdown("**Тип связи:**")
        relation_type = st.radio(
            "Выберите тип",
            ["1:1", "1:N", "N:1", "M:N"],
            key="relation_type_select",
            horizontal=True,
            help="1:N — одна запись слева связана с многими справа",
        )

        # Row 3: To
        st.markdown("**Куда (To):**")
        r3_c1, r3_c2 = st.columns(2)
        with r3_c1:
            to_table = st.selectbox(
                "Таблица",
                table_names,
                key="to_table_select",
                index=1 if len(table_names) > 1 else 0,
            )
        with r3_c2:
            to_cols = table_columns[to_table]
            to_column = st.selectbox(
                "Колонка", to_cols, key="to_column_select", index=0
            )

        # Ошибки
        if st.session_state.form_error:
            st.error(st.session_state.form_error)

        # Кнопки
        st.divider()
        act_1, act_2, _ = st.columns([1, 1, 4])
        with act_1:
            st.button(
                "💾 Сохранить",
                type="primary",
                on_click=create_relation_callback,
                use_container_width=True,
            )
        with act_2:
            st.button(
                "❌ Отмена", on_click=reset_form_callback, use_container_width=True
            )

    st.divider()

# 3. Список связей
st.subheader("Активные связи")
relations = relation_service.get_all_relations()

if not relations:
    st.info("Связей нет. Создайте первую!")
else:
    for rel in relations:
        with st.container(border=True):
            col_left, col_right = st.columns([4, 1])

            with col_left:
                # Визуализация связи
                type_icon = {
                    "1:1": "↔️",
                    "1:N": "→",
                    "N:1": "←",
                    "M:N": "⇄",
                }.get(rel.relation_type, "→")

                st.markdown(
                    f"**{rel.from_table}.{rel.from_column}** "
                    f"{type_icon} **{rel.relation_type}** "
                    f"**{rel.to_table}.{rel.to_column}**"
                )
                st.caption(f"ID: {rel.id}")

            with col_right:
                if st.button("🗑️", key=f"del_rel_{rel.id}"):
                    relation_service.delete_relation(rel.id)
                    st.rerun()

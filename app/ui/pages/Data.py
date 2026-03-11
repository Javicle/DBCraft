import streamlit as st
import pandas as pd
from sqlalchemy import Engine, text
from app.ui.deps import get_services
from app.domain.service import TableService

st.set_page_config(page_title="Данные", page_icon="🗂️", layout="wide")

services = get_services()
table_service: TableService = services["table_service"]  # type: ignore
engine: Engine = services["engine"]  # type: ignore

st.title("🗂️ Просмотр данных")

# 1. Выбор таблицы
tables = table_service.get_all_tables()
if not tables:
    st.warning("Нет таблиц. Создайте сначала таблицу.")
    st.stop()

table_names = [t.name for t in tables]
selected_table = st.selectbox("Выберите таблицу", table_names)

# 2. Отображение данных
if selected_table:
    try:
        with engine.connect() as conn:
            df = pd.read_sql(f"SELECT * FROM {selected_table}", conn)

        st.subheader(f"Данные: {selected_table}")
        st.dataframe(df, use_container_width=True)

        st.divider()

        # 3. Добавление записи
        st.subheader("➕ Добавить запись")
        with st.form(f"add_row_{selected_table}"):
            # Динамические поля на основе колонок таблицы
            table_obj = next(t for t in tables if t.name == selected_table)
            inputs = {}
            cols = st.columns(len(table_obj.columns))

            for idx, col in enumerate(table_obj.columns):
                with cols[idx]:
                    if col.column_type == "BOOLEAN":
                        inputs[col.name] = st.checkbox(col.name)
                    elif col.column_type in ("INT", "FLOAT"):
                        inputs[col.name] = st.number_input(
                            col.name, key=f"inp_{col.name}"
                        )
                    else:
                        inputs[col.name] = st.text_input(
                            col.name, key=f"inp_{col.name}"
                        )

            if st.form_submit_button("Сохранить"):
                # Формирование INSERT
                columns = list(inputs.keys())
                values = list(inputs.values())
                placeholders = ", ".join([":val_" + str(i) for i in range(len(values))])
                sql = text(f"""
                    INSERT INTO {selected_table} ({", ".join(columns)})
                    VALUES ({placeholders})
                """)
                params = {f"val_{i}": v for i, v in enumerate(values)}

                with engine.begin() as conn:
                    conn.execute(sql, params)

                st.success("Запись добавлена!")
                st.rerun()

        # 4. Экспорт
        csv = df.to_csv(index=False).encode("utf-8")
        st.download_button("📥 Скачать CSV", csv, f"{selected_table}.csv", "text/csv")

    except Exception as e:
        st.error(f"Ошибка: {e}")

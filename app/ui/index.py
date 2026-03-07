import numpy as np
import pandas as pd
import streamlit as st

from app.ui.pyvis_test import render_db_schema

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
render_db_schema(service.get_all_tables(), relations_service.get_all())

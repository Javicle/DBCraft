import streamlit as st

from app.infrastructure.di import create_services


@st.cache_resource
def get_services():
    return create_services()

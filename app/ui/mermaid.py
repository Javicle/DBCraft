import streamlit as st
import streamlit_mermaid as stmd

er_code = """
erDiagram
    USER ||--o{ ORDER : "делает"
    ORDER ||--|{ LINE-ITEM : "содержит"
    PRODUCT ||--o{ LINE-ITEM : "включен в"
    
    USER {
        string username PK
        string email
        string password
    }
    
    ORDER {
        int id PK
        string delivery_address
        datetime created_at
    }
    PRODUCT {
        int id PK
        string name
        float price
    }
    LINE-ITEM {
        int order_id FK
        int product_id FK
        int quantity
    }
"""
stmd.st_mermaid(er_code)

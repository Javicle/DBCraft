import streamlit.components.v1 as components
from pyvis.network import Network
import streamlit as st
from app.domain.entities import Relation, TableSchema
import json


def render_db_schema(
    tables: list[TableSchema], relations: list[Relation], layout: str = "Physics"
):
    """
    Визуализация схемы БД.
    layout: "Physics" (свободное перемещение) или "Hierarchical" (структура сверху вниз)
    """
    net = Network(
        height="600px",
        width="100%",
        bgcolor="#0E1117",  # Темная тема Streamlit
        directed=True,
    )

    # Настройки физики и отображения
    if layout == "Hierarchical":
        options = {
            "layout": {
                "hierarchical": {
                    "enabled": True,
                    "direction": "UD",
                    "sortMethod": "directed",
                    "nodeSpacing": 200,
                    "levelSeparation": 150,
                }
            },
            "physics": {"enabled": False},
        }
    else:
        # Плавная физика для "перетаскивания"
        options = {
            "physics": {
                "forceAtlas2Based": {
                    "gravitationalConstant": -50,
                    "centralGravity": 0.01,
                    "springLength": 100,
                    "springConstant": 0.08,
                },
                "maxVelocity": 50,
                "solver": "forceAtlas2Based",
                "timestep": 0.35,
                "stabilization": {"iterations": 150},
            },
            "edges": {
                "smooth": {
                    "type": "cubicBezier",
                    "forceDirection": "horizontal",
                    "roundness": 0.4,
                }
            },
        }

    json_options = json.dumps(options)
    net.set_options(f"var options = {json_options}")

    for table in tables:
        # Формируем текст внутри узла
        # Помечаем PK ключиком
        cols_text = ""
        for c in table.columns:
            pk_mark = "🔑 " if c.primary_key else "  "
            cols_text += f"{pk_mark}{c.name} : {c.column_type}\n"

        label = f"{table.name}\n{'-' * (len(table.name) + 4)}\n{cols_text}"

        net.add_node(
            table.name,
            label=label,
            shape="box",
            color={
                "background": "#1E293B",
                "border": "#34d399",
                "highlight": {"background": "#34d399", "border": "#FFFFFF"},
            },
            font={"face": "monospace", "align": "left", "size": 14, "color": "#FFFFFF"},
            margin=10,
            borderWidth=2,
        )

    for rel in relations:
        # Разные цвета для разных типов связей
        color = "#60A5FA" if rel.relation_type == "1:N" else "#F87171"
        if rel.relation_type == "M:N":
            color = "#A78BFA"

        net.add_edge(
            rel.from_table,
            rel.to_table,
            label=rel.relation_type,
            color=color,
            width=2,
            font={"size": 10, "color": "#94A3B8", "strokeWidth": 0},
        )

    # Генерация и рендер
    try:
        html = net.generate_html()
        components.html(html, height=620)
    except Exception as e:
        st.error(f"Ошибка визуализации: {e}")

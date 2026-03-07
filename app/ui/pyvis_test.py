from __future__ import annotations

import streamlit.components.v1 as components
from pyvis.network import Network

from app.domain.entities import Relation, TableSchema


def render_db_schema(tables: list[TableSchema], relations: list[Relation]):
    net = Network(
        height="600px",
        width="100%",
        bgcolor="#0E1117",
        font_color="white",
        directed=True,
    )

    # Настройки иерархии (лучше для БД)
    net.set_options("""
    var options = {
      "layout": { "hierarchical": { "enabled": true, "direction": "UD", "sortMethod": "directed" } },
      "physics": { "enabled": false }
    }
    """)

    for table in tables:
        cols_text = "\n".join(
            [f"{c.name}: {c.column_type}" for c in table.columns[:5]]
        )  # Лимит 5 полей
        label = f"{table.name}\n---\n{cols_text}"

        net.add_node(
            table.name,  # ID = имя таблицы
            label=label,
            shape="box",
            color="#34d399",
            font={"face": "monospace", "align": "left", "size": 14},
        )

    for rel in relations:
        net.add_edge(rel.from_table, rel.to_table, label=rel.type, arrows="to")

    html = net.generate_html()
    components.html(html, height=620)

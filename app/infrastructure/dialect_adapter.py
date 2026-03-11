from sqlalchemy import Engine


class DialectAdapter:
    def __init__(self, engine: Engine) -> None:
        self.name = engine.dialect

    @property
    def supports_alter_constraint(self) -> bool:
        return self.name in ("postgresql", "mysql")

    @property
    def supports_cascade_delete(self) -> bool:
        """Поддерживается ли CASCADE при удалении."""
        return self.name in ("postgresql", "mysql")

    @property
    def requires_junction_for_mn(self) -> bool:
        """Нужна ли отдельная таблица для M:N (везде да)."""
        return True

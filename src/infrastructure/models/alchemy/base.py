from typing import Any

from sqlalchemy import JSON, MetaData
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    type_annotation_map = {dict[str, Any]: JSON}

    # Do not include schema name. Alembic recreates foreign keys in all migrations
    metadata = MetaData()

    # Automatically generate id column
    id: Mapped[int] = mapped_column(primary_key=True)

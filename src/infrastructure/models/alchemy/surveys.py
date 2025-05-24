from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import JSON, DateTime, Enum, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from domain.entities.enums import CityCategory, SurveyStatus
from infrastructure.models.alchemy.base import Base

if TYPE_CHECKING:
    from infrastructure.models.alchemy.users import User


class Survey(Base):
    __tablename__ = "surveys"

    name: Mapped[str] = mapped_column(String, index=True)
    author_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.now, onupdate=datetime.now, nullable=False
    )

    status: Mapped[SurveyStatus] = mapped_column(
        Enum(SurveyStatus, name="survey_status", native_enum=False),
        nullable=False,
        default=SurveyStatus.DRAFT,
    )
    city: Mapped[str] = mapped_column(
        Enum(CityCategory, name="route_city", native_enum=False, length=16),
        index=True,
        default=CityCategory.PERM,
    )

    data: Mapped[dict | None] = mapped_column(JSON, default=None, server_default=None)
    places: Mapped[dict | None] = mapped_column(JSON, default=None, server_default=None)

    author: Mapped["User"] = relationship("User", back_populates="surveys")

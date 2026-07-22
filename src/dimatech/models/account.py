from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, Numeric
from sqlalchemy.orm import Mapped, mapped_column, relationship

from dimatech.db.base import Base

if TYPE_CHECKING:
    from dimatech.models.payment import Payment
    from dimatech.models.user import User


class Account(Base):
    __tablename__ = "accounts"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    balance: Mapped[Decimal] = mapped_column(
        Numeric[Decimal](12, 2),
        default=Decimal("0.00"),
        server_default="0.00",
    )

    user: Mapped["User"] = relationship(back_populates="accounts")
    payments: Mapped[list["Payment"]] = relationship(
        back_populates="account",
        cascade="all, delete-orphan",
    )

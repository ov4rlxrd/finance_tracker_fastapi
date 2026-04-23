from datetime import datetime, timezone
from decimal import Decimal

from pydantic import model_validator
from sqlalchemy import ForeignKey, String, UniqueConstraint, Index, text, Integer, DateTime

from app.core.enums import CurrencyEnum
from app.database import Model
from sqlalchemy.orm import Mapped, mapped_column, relationship


class User(Model):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(120), nullable=False)
    email: Mapped[str] = mapped_column(String(120), nullable=False)
    password_hash: Mapped[str] = mapped_column(String(200),nullable=False)
    role: Mapped[str] = mapped_column(default="user", nullable=False)
    is_active: Mapped[bool] = mapped_column(default=True, nullable=False)
    is_verified: Mapped[bool] = mapped_column(default=False, nullable=False)

    wallets: Mapped[list[Wallet]] = relationship(back_populates="user", cascade="all, delete-orphan", lazy="selectin")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), default=None, nullable=True)

    reset_tokens: Mapped[list[PasswordResetToken]] = relationship(back_populates="user", cascade="all, delete-orphan")



class Wallet(Model):
    __tablename__ = 'wallets'
    __table_args__ = (Index(
            'uq_wallet_user_name_active',
            'user_id', 'name',
            unique=True,
            postgresql_where=text("deleted_at IS NULL")
        ),)

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
    balance: Mapped[Decimal] = mapped_column(default=Decimal(0), nullable=False)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    currency: Mapped[CurrencyEnum] = mapped_column(default=CurrencyEnum.RUB, nullable=False)
    is_active: Mapped[bool] = mapped_column(default=True, nullable=False)

    user: Mapped[User] = relationship(back_populates="wallets")

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), default=None, nullable=True)


class Operation(Model):
    __tablename__ = 'operations'

    id: Mapped[int] = mapped_column(primary_key=True)
    wallet_id: Mapped[int] = mapped_column(ForeignKey("wallets.id"), nullable=False)
    operation_type: Mapped[str]
    amount: Mapped[Decimal]
    currency: Mapped[CurrencyEnum] = mapped_column(default=CurrencyEnum.RUB, nullable=False)
    category: Mapped[str | None] = mapped_column(default=None)
    subcategory: Mapped[str | None] = mapped_column(default=None)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)


class PasswordResetToken(Model):
    __tablename__ = 'password_reset_tokens'
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    token_hash: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)

    user: Mapped[User] = relationship(back_populates="reset_tokens")



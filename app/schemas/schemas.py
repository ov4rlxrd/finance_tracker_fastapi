from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, Field, ConfigDict, field_validator, EmailStr

from app.core.enums import CurrencyEnum


class UserBase(BaseModel):
    username: str = Field(max_length=127)
    email: EmailStr = Field(max_length=120)



class UserCreate(UserBase):
    password: str = Field(min_length=8)
    initial_wallet_name:str = Field(default="Main", max_length=127)
    initial_wallet_balance:Decimal = Field(default=Decimal("0"), ge=0)

class UserResponse(UserBase):
    id: int
    wallets: list[WalletResponse]
    role: str
    model_config = ConfigDict(from_attributes=True)


class UserAdminResponse(UserResponse):
    is_active: bool

    wallets: list[WalletResponse]
    created_at: datetime  | None = Field(None)
    deleted_at: datetime | None = Field(None)

class UserUpdate(BaseModel):
    username: str = Field(max_length=127)

class Token(BaseModel):
    access_token: str
    token_type: str


class OperationBase(BaseModel):
    wallet_name: str = Field(..., max_length=127)
    amount: Decimal = Field(default=Decimal("0"), ge=0)
    category: str | None = Field(None,max_length=255)

    @field_validator("amount")
    def amount_validator(cls, v: float) -> float:
        if v <= 0:
            raise ValueError("Amount must be positive")
        return v

    @field_validator("wallet_name")
    def wallet_name_validator(cls, v: str) -> str:
        v = v.strip()

        if not v:
            raise ValueError("Wallet name cannot be empty")

        return v

class OperationRequest(OperationBase):
     pass

class OperationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    wallet_id: int
    operation_type: str
    amount: Decimal
    currency: CurrencyEnum
    category: str | None
    subcategory: str | None

    created_at: datetime



class WalletBase(BaseModel):
    name: str = Field(..., max_length=127)
    balance:Decimal = Field(default=Decimal("0"), ge=0)
    currency: CurrencyEnum = CurrencyEnum.RUB
    model_config = ConfigDict(from_attributes=True)



    @field_validator("name")
    def wallet_name_validator(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("Wallet name cannot be empty")
        return v

    @field_validator("balance")
    def initial_balance_validator(cls, v: float) -> float:
        if v < 0:
            raise ValueError("Initial balance must be positive")
        return v


class WalletCreate(BaseModel):
    name: str = Field(..., max_length=127)
    currency: CurrencyEnum = CurrencyEnum.RUB


class WalletDelete(BaseModel):
    name: str = Field(..., max_length=127)

class WalletTotalBalanceResponse(BaseModel):
    name: str
    balance: Decimal
    currency: CurrencyEnum

class WalletUpdate(BaseModel):
    old_name: str = Field(..., max_length=127)
    new_name: str = Field(..., max_length=127)
    

class WalletResponse(BaseModel):
    id:int
    name: str
    balance: Decimal
    currency: CurrencyEnum
    model_config = ConfigDict(from_attributes=True)




class IternalTransferCreateSchema(BaseModel):
    from_wallet_id: int
    to_wallet_id: int
    amount: Decimal



class TransferCreateSchema(BaseModel):
    to_user_id: int
    wallet_id: int
    amount: Decimal


class ForgotPasswordRequest(BaseModel):
    email: EmailStr = Field(max_length=127)


class ForgotPasswordEmailData(BaseModel):
    to_email: EmailStr
    username: str
    token: str

class ResetPasswordRequest(BaseModel):
    token:str
    new_password:str = Field(min_length=8)

class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str = Field(min_length=8)
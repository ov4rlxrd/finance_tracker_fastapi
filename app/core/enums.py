from enum import StrEnum, auto


class CurrencyEnum(StrEnum):
    RUB = auto()
    USD = auto()
    EUR = auto()

class OperationEnum(StrEnum):
    INCOME = auto()
    EXPENSE = auto()
    TRANSFER_OUT = auto()
    TRANSFER_IN = auto()
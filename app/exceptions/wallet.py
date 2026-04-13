from starlette import status

from app.exceptions.base import AppException


class WalletNotFound(AppException):
    status_code = status.HTTP_404_NOT_FOUND
    detail = "Wallet not found."

class WalletAlreadyExists(AppException):
    status_code = status.HTTP_400_BAD_REQUEST
    detail = "Wallet already exists."

class TransferSameWallet(AppException):
    status_code = status.HTTP_400_BAD_REQUEST
    detail = "Cannot transfer same wallet."

class InsufficientFunds(AppException):
    status_code = status.HTTP_400_BAD_REQUEST
    detail = "Insufficient funds"

class CurrencyConversionError(AppException):
    status_code = status.HTTP_400_BAD_REQUEST
    detail = "Currency conversion error"


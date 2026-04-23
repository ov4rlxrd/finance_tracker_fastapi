from starlette import status
from app.exceptions.base import AppException

class UserAlreadyExists(AppException):
    status_code = status.HTTP_400_BAD_REQUEST
    detail = 'User already exists.'

class EmailAlreadyExists(AppException):
    status_code = status.HTTP_400_BAD_REQUEST
    detail = 'Email already exists.'

class UserNotFound(AppException):
    status_code = status.HTTP_404_NOT_FOUND
    detail = 'User not found.'

class UserIsDisabled(AppException):
    status_code = status.HTTP_403_FORBIDDEN
    detail = 'User is disabled.'

class NotAuthorized(AppException):
    status_code = status.HTTP_401_UNAUTHORIZED
    detail = "Not authorized"

class ResetTokenException(AppException):
    status_code = status.HTTP_400_BAD_REQUEST
    detail = 'Invalid or expired reset token'

class PasswordIncorrect(AppException):
    status_code = status.HTTP_400_BAD_REQUEST
    detail = 'Incorrect password'

class InvalidToken(AppException):
    status_code = status.HTTP_401_UNAUTHORIZED
    detail = 'Invalid or Expired token'

class AccountNotVerified(AppException):
    status_code = status.HTTP_401_UNAUTHORIZED
    detail = 'Account not verified'
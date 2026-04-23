from starlette import status

from app.exceptions.base import AppException



class RateException(AppException):
    status_code = status.HTTP_400_BAD_REQUEST
    detail = 'Rate not found'
from starlette import status


class AppException(Exception):
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    detail = "Internal Server Error"
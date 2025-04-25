# helpers/response_helpers.py

from rest_framework import status
from rest_framework.response import Response


def success_response(data=None, message="Success", status_code=200):
    """
    Standard format for successful responses.

    :param data: The data to send back in the response (default is None).
    :param message: The success message (default is "Success").
    :param status_code: The HTTP status code (default is HTTP 200 OK).
    :return: A Response object.
    """
    response_data = {
        "status": "success",
        "message": message,
        "data": data if data else None
    }
    return Response(response_data, status=status_code)


def error_response(message, status_code=400, errors=None):
    """
    Standard format for error responses.

    :param message: The error message to send back.
    :param status_code: The HTTP status code for the error (default is HTTP 400 Bad Request).
    :param errors: Detailed errors (default is None).
    :return: A Response object.
    """
    response_data = {
        "status": "error",
        "message": message,
        "errors": errors if errors else None
    }
    return Response(response_data, status=status_code)

from typing import Any, Callable, Optional
from fastapi import FastAPI, status
from fastapi.requests import Request
from fastapi.responses import JSONResponse

class SomeKindOfException(Exception):
    """Base class for all Some Kind of Monster Exceptions"""
    def __init__(self, info:Optional[dict]=""):
        self.info = info

class UserAlreadyExists(SomeKindOfException):
    """The user have registered informations that already exists"""

class UserNotFound(SomeKindOfException):
    """No User have been found with this informations"""

class InvalidCredentials(SomeKindOfException):
    """User have provided wrong informations during login """

class UserNotVerified(SomeKindOfException):
    """User have not been verified yet"""

class TokenDecodeFail(SomeKindOfException):
    """Something went wrong when decoding the authentification token"""

class UpdateNotAllowed(SomeKindOfException):
    """This update is not allowed"""

class InsufficientPermission(SomeKindOfException):
    """The user dont have enough permission to performed this action"""

class RoleNotFound(SomeKindOfException):
    """No role have been found with this name"""

class BookNotFound(SomeKindOfException):
    """Book Not Found"""

class BookAlreadyRegistered(SomeKindOfException):
    """The user already have this book registered"""

class UserVerificationFailed(SomeKindOfException):
    """Something went wrong during user verification by email"""

class ResetPasswordDontMatch(SomeKindOfException):
    """The confirm password doesnt match the new password"""

class UpdateRequestNotAllowed(SomeKindOfException):
    "This update request is not allowed"

class RequestCheckNotAllowed(SomeKindOfException):
    """The user cant check this request"""

class RequestNotFound(SomeKindOfException):
    """Request not found"""
    
def create_exception_handler(status_code:int, initial_details:Any) -> Callable[[Request, Exception], JSONResponse]:
    async def exception_handler(request: Request, exception: SomeKindOfException):
        return JSONResponse(
            content= {
                "initial_details": initial_details,
                "info": exception.__dict__.get("info")
            },
            status_code=status_code
        )
    return exception_handler

def register_errors(app:FastAPI):
    app.add_exception_handler(
        UserAlreadyExists,
        create_exception_handler(
            status_code=status.HTTP_409_CONFLICT,
            initial_details={
                "message": UserAlreadyExists.__doc__,
                "error_code":"user_already_exist"
            }
        )
    )

    app.add_exception_handler(
        UserNotFound,
        create_exception_handler(
            status_code=status.HTTP_404_NOT_FOUND,
            initial_details={
                "message": UserNotFound.__doc__,
                "error_code":"user_not_found"
            }
        )
    )

    app.add_exception_handler(
        InvalidCredentials,
        create_exception_handler(
            status_code=status.HTTP_404_NOT_FOUND,
            initial_details={
                "message": InvalidCredentials.__doc__,
                "error_code":"user_not_found"
            }
        )
    )

    app.add_exception_handler(
        UserNotVerified,
        create_exception_handler(
            status_code=status.HTTP_403_FORBIDDEN,
            initial_details={
                "message": UserNotVerified.__doc__,
                "error_code":"user_not_verified"
            }
        )
    )

    app.add_exception_handler(
        TokenDecodeFail,
        create_exception_handler(
            status_code=status.HTTP_401_UNAUTHORIZED,
            initial_details={
                "message": TokenDecodeFail.__doc__,
                "error_code":"token_decode_fail"
            }
        )
    )

    app.add_exception_handler(
        UpdateNotAllowed,
        create_exception_handler(
            status_code=status.HTTP_403_FORBIDDEN,
            initial_details={
                "message": UpdateNotAllowed.__doc__,
                "error_code":"update_not_allowed"
            }
        )
    )

    app.add_exception_handler(
        InsufficientPermission,
        create_exception_handler(
            status_code=status.HTTP_403_FORBIDDEN,
            initial_details={
                "message": InsufficientPermission.__doc__,
                "error_code": "insufficient_permission"
            }
        )
    )

    app.add_exception_handler(
        RoleNotFound,
        create_exception_handler(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            initial_details={
                "message": RoleNotFound.__doc__,
                "error_code": "role_not_found"
            }
        )
    )

    app.add_exception_handler(
        BookNotFound,
        create_exception_handler(
            status_code=status.HTTP_404_NOT_FOUND,
            initial_details={
                "message": BookNotFound.__doc__,
                "error_code": "book_not_found"
            }
        )
    )

    app.add_exception_handler(
        BookAlreadyRegistered,
        create_exception_handler(
            status_code=status.HTTP_400_BAD_REQUEST,
            initial_details={
                "message": BookAlreadyRegistered.__doc__,
                "error_code": "book_already_registered"
            }
        )
    )

    app.add_exception_handler(
        UserVerificationFailed,
        create_exception_handler(
            status_code=status.HTTP_417_EXPECTATION_FAILED,
            initial_details={
                "message": UserVerificationFailed.__doc__,
                "error_code": "user_verification_failed"
            }
        )
    )

    app.add_exception_handler(
        ResetPasswordDontMatch,
        create_exception_handler(
            status_code=status.HTTP_400_BAD_REQUEST,
            initial_details={
                "message": ResetPasswordDontMatch.__doc__,
                "error_code":"password_reset_dont_match"
            }
        )
    )

    app.add_exception_handler(
        UpdateRequestNotAllowed,
        create_exception_handler(
            status_code=status.HTTP_403_FORBIDDEN,
            initial_details={
                "message": UpdateRequestNotAllowed.__doc__,
                "error_code":"update_request_not_allowed"
            }
        )
    )

    app.add_exception_handler(
        RequestCheckNotAllowed,
        create_exception_handler(
            status_code=status.HTTP_403_FORBIDDEN,
            initial_details={
                "message": RequestCheckNotAllowed.__doc__,
                "error_code":"request_check_not_allowed"
            }
        )
    )

    app.add_exception_handler(
        RequestNotFound,
        create_exception_handler(
            status_code=status.HTTP_403_FORBIDDEN,
            initial_details={
                "message": RequestNotFound.__doc__,
                "error_code":"request_not_found"
            }
        )
    )
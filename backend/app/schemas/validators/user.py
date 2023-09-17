from typing import Any

from pydantic import WrapValidator, AfterValidator
from pydantic_core.core_schema import ValidationInfo, ValidatorFunctionWrapHandler

__all__ = [
    'PasswordValidator'
]

from app.consts.http import HttpResp
from app.core.exceptions import AppException


def password_len(passwd: str) -> str:
    if not (6 <= len(passwd) <= 20):
        raise AppException(HttpResp.FAILED, msg='密码必须在6~20位')
    return passwd


PasswordValidator = AfterValidator(password_len)

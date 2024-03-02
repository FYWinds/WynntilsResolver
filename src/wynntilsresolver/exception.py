"""
Author       : FYWinds i@windis.cn
Date         : 2024-02-28 22:32:44
LastEditors  : FYWinds i@windis.cn
LastEditTime : 2024-02-29 16:20:17
FilePath     : /src/wynntilsresolver/exception.py
"""


class ResolverException(Exception):
    def __init__(self, message: str):
        super().__init__(message)


class ParseFailed(ResolverException):
    def __init__(self, message: str):
        super().__init__(message)


class ResolverDefinitionError(ResolverException):
    def __init__(self, message: str):
        super().__init__(message)


class InvalidStartByte(ResolverException):
    def __init__(self, message: str):
        super().__init__(message)


class InvalidItemType(ResolverException):
    def __init__(self, message: str):
        super().__init__(message)


class MissingInfo(ResolverException):
    def __init__(self, message: str):
        super().__init__(message)

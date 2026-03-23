from enum import Enum, auto


class TokenType(Enum):
    PRINT = auto()
    STRING = auto()
    SEMICOLON = auto()
    EOF = auto()

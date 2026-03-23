from enum import Enum, auto


class TokenType(Enum):
    PRINT = auto()
    STRING = auto()
    NUMBER = auto()
    LEFT_PAREN = auto()
    RIGHT_PAREN = auto()
    PLUS = auto()
    MINUS = auto()
    STAR = auto()
    SLASH = auto()
    SEMICOLON = auto()
    EOF = auto()

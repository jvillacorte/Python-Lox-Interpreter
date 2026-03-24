from enum import Enum, auto
#defines tokens used by scanner/parser, initialized with auto() to automatically assign values later on
class TokenType(Enum):
    PRINT = auto()
    IF = auto()
    ELSE = auto()
    WHILE = auto()
    FOR = auto()

    FUN = auto()
    RETURN = auto()
    
    VAR = auto()
    STRING = auto()
    NUMBER = auto()
    IDENTIFIER = auto()
    EQUAL = auto()
    COMMA = auto()
    
    LEFT_BRACE = auto()
    RIGHT_BRACE = auto()
    LEFT_PAREN = auto()
    RIGHT_PAREN = auto()
    
    PLUS = auto()
    MINUS = auto()
    STAR = auto()
    SLASH = auto()

    BANG = auto()
    BANG_EQUAL = auto()
    EQUAL_EQUAL = auto()
    LESS = auto()
    LESS_EQUAL = auto()
    GREATER = auto()
    GREATER_EQUAL = auto()

    AND = auto()
    OR = auto()
    TRUE = auto()
    FALSE = auto()

    NIL = auto()
    SEMICOLON = auto()
    EOF = auto()

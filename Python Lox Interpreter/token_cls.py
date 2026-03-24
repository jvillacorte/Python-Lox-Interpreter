from dataclasses import dataclass
from token_type import TokenType

#defines token data object that scanner produces and parser consumes
@dataclass(frozen=True)
class Token:
    type: TokenType
    lexeme: str
    literal: object
    line: int
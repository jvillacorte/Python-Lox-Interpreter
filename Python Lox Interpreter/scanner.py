from token_cls import Token
from token_type import TokenType
from error import error


class Scanner:
    def __init__(self, source: str):
        self.source = source
        self.tokens: list[Token] = []
        self.start = 0
        self.current = 0
        self.line = 1

    def scan_tokens(self) -> list[Token]:
        while not self.is_at_end():
            self.start = self.current
            self.scan_token()

        self.tokens.append(Token(TokenType.EOF, "", None, self.line))
        return self.tokens

    def scan_token(self) -> None:
        c = self.advance()

        if c in (" ", "\r", "\t"):
            return
        if c == "\n":
            self.line += 1
            return
        if c == ";":
            self.add_token(TokenType.SEMICOLON)
            return
        if c == '"':
            self.scan_string()
            return
        if c.isalpha() or c == "_":
            self.scan_identifier()
            return

        error(self.line, msg="Unexpected character.")

    def scan_string(self) -> None:
        while self.peek() != '"' and not self.is_at_end():
            if self.peek() == "\n":
                self.line += 1
            self.advance()

        if self.is_at_end():
            error(self.line, msg="Unterminated string.")
            return

        self.advance()  # closing quote
        value = self.source[self.start + 1:self.current - 1]
        self.add_token(TokenType.STRING, value)

    def scan_identifier(self) -> None:
        while self.peek().isalnum() or self.peek() == "_":
            self.advance()

        text = self.source[self.start:self.current]
        if text == "print":
            self.add_token(TokenType.PRINT)
            return

        error(self.line, msg=f"Unexpected identifier '{text}'.")

    def add_token(self, token_type: TokenType, literal: object = None) -> None:
        lexeme = self.source[self.start:self.current]
        self.tokens.append(Token(token_type, lexeme, literal, self.line))

    def is_at_end(self) -> bool:
        return self.current >= len(self.source)

    def advance(self) -> str:
        ch = self.source[self.current]
        self.current += 1
        return ch

    def peek(self) -> str:
        if self.is_at_end():
            return "\0"
        return self.source[self.current]
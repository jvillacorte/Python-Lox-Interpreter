from token_cls import Token
from token_type import TokenType
from error import error


KEYWORDS = {
    "print": TokenType.PRINT,
    "if": TokenType.IF,
    "else": TokenType.ELSE,
    "while": TokenType.WHILE,
    "for": TokenType.FOR,
    "fun": TokenType.FUN,
    "return": TokenType.RETURN,
    "var": TokenType.VAR,
    "and": TokenType.AND,
    "or": TokenType.OR,
    "true": TokenType.TRUE,
    "false": TokenType.FALSE,
    "nil": TokenType.NIL,
}


class Scanner:
    #initializes scanner state
    def __init__(self, source: str):
        self.source = source
        self.tokens: list[Token] = []
        self.start = 0
        self.current = 0
        self.line = 1

    #scans source code into tokens, returns list of tokens
    def scan_tokens(self) -> list[Token]:
        while not self.is_at_end():
            self.start = self.current
            self.scan_token()

        self.tokens.append(Token(TokenType.EOF, "", None, self.line))
        return self.tokens

    #scans single token, adds to list of tokens, handles errors
    #reads one character with advance, handles whitespace/newline
    #if nothing matches return unexpected character error
    def scan_token(self) -> None:
        c = self.advance()

        if c in (" ", "\r", "\t"):
            return
        if c == "\n":
            self.line += 1
            return
        if c == "(":
            self.add_token(TokenType.LEFT_PAREN)
            return
        if c == ")":
            self.add_token(TokenType.RIGHT_PAREN)
            return
        if c == ",":
            self.add_token(TokenType.COMMA)
            return
        if c == "{":
            self.add_token(TokenType.LEFT_BRACE)
            return
        if c == "}":
            self.add_token(TokenType.RIGHT_BRACE)
            return
        if c == "+":
            self.add_token(TokenType.PLUS)
            return
        if c == "-":
            self.add_token(TokenType.MINUS)
            return
        if c == "*":
            self.add_token(TokenType.STAR)
            return
        if c == "/":
            if self.peek() == "/":
                # Consume comment text until end of line.
                while self.peek() != "\n" and not self.is_at_end():
                    self.advance()
            else:
                self.add_token(TokenType.SLASH)
            return
        if c == "!":
            if self.peek() == "=":
                self.advance()
                self.add_token(TokenType.BANG_EQUAL)
            else:
                self.add_token(TokenType.BANG)
            return
        if c == "=":
            if self.peek() == "=":
                self.advance()
                self.add_token(TokenType.EQUAL_EQUAL)
            else:
                self.add_token(TokenType.EQUAL)
            return
        if c == "<":
            if self.peek() == "=":
                self.advance()
                self.add_token(TokenType.LESS_EQUAL)
            else:
                self.add_token(TokenType.LESS)
            return
        if c == ">":
            if self.peek() == "=":
                self.advance()
                self.add_token(TokenType.GREATER_EQUAL)
            else:
                self.add_token(TokenType.GREATER)
            return
        if c == ";":
            self.add_token(TokenType.SEMICOLON)
            return
        if c == '"':
            self.scan_string()
            return
        if c.isdigit():
            self.scan_number()
            return
        if c.isalpha() or c == "_":
            self.scan_identifier()
            return

        error(self.line, msg="Unexpected character.")

    #consumes characters until closing quote/EOF
    #tracks line count if newline appears
    #reports unterminated string if EOF is reached before closing quote
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

    #lexes identifiers and keywords
    def scan_identifier(self) -> None:
        while self.peek().isalnum() or self.peek() == "_":
            self.advance()

        text = self.source[self.start:self.current]
        keyword_type = KEYWORDS.get(text)
        if keyword_type is not None:
            self.add_token(keyword_type)
            return

        self.add_token(TokenType.IDENTIFIER)

    #lexes numeric literals
    def scan_number(self) -> None:
        while self.peek().isdigit():
            self.advance()

        if self.peek() == "." and self.peek_next().isdigit():
            self.advance()
            while self.peek().isdigit():
                self.advance()

        value = float(self.source[self.start:self.current])
        self.add_token(TokenType.NUMBER, value)

    #creates/stores one token
    def add_token(self, token_type: TokenType, literal: object = None) -> None:
        lexeme = self.source[self.start:self.current]
        self.tokens.append(Token(token_type, lexeme, literal, self.line))

    #helper functions for scanning
    def is_at_end(self) -> bool:
        return self.current >= len(self.source)

    #consumes current character and advances position
    def advance(self) -> str:
        ch = self.source[self.current]
        self.current += 1
        return ch

    #looks at current character without consuming it, returns null char if at end of source
    def peek(self) -> str:
        if self.is_at_end():
            return "\0"
        return self.source[self.current]

    #looks at next character without consuming it, returns null char if at end of source
    def peek_next(self) -> str:
        if self.current + 1 >= len(self.source):
            return "\0"
        return self.source[self.current + 1]
from token_type import TokenType
from expressions import Literal
from statements import Print, Stmt
from error import ParseErr, error


class Parser:
    #sets up token list for parsing
    def __init__(self, tokens):
        self.tokens = tokens
        self.cur = 0

    #repeats statements until EOF hit
    #returns list of statement nodes for interpreter.pt to execute
    def parse(self) -> list[Stmt]:
        stmts: list[Stmt] = []
        while not self.tok_end():
            stmts.append(self.statement())
        return stmts

    #parses statement, worky only print
    def statement(self) -> Stmt:
        if self.match(TokenType.PRINT):
            return self.print_statement()

        tok = self.peek()
        error(tok.line, tok, "Expected 'print'.")
        raise ParseErr()

    #parse body of print statement, calls expression() for value, then checks for semicolon
    def print_statement(self) -> Stmt:
        value = self.expression()
        self.consume(TokenType.SEMICOLON, "Expected ';' after value.")
        return Print(value)

    #parses expression, string literals rn
    def expression(self):
        if self.match(TokenType.STRING):
            return Literal(self.previous().literal)

        tok = self.peek()
        error(tok.line, tok, "Expected string literal.")
        raise ParseErr()


    def match(self, *types: TokenType) -> bool:
        for t in types:
            if self.check(t):
                self.advance()
                return True
        return False

    #consume checks for expected token type
    def consume(self, token_type: TokenType, msg: str):
        if self.check(token_type):
            return self.advance()
        tok = self.peek()
        error(tok.line, tok, msg)
        raise ParseErr()

    #looks at current token and checks if it matches expected type, returns false if EOF
    def check(self, token_type: TokenType) -> bool:
        if self.tok_end():
            return False
        return self.peek().type == token_type

    #move cursor forward one token if the token isn't EOF, returns previous token
    def advance(self):
        if not self.tok_end():
            self.cur += 1
        return self.previous()

    #true when token is EOF, prevents going past end of token list
    def tok_end(self) -> bool:
        return self.peek().type == TokenType.EOF

    def peek(self):
        return self.tokens[self.cur]

    def previous(self):
        return self.tokens[self.cur - 1]
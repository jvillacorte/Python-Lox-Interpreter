from token_type import TokenType
from expressions import Assign, Binary, Grouping, Literal, Logical, Unary, Variable
from statements import Expression, Print, Stmt, Var
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
            stmts.append(self.declaration())
        return stmts

    def declaration(self) -> Stmt:
        if self.match(TokenType.VAR):
            return self.var_declaration()
        return self.statement()

    def var_declaration(self) -> Stmt:
        name = self.consume(TokenType.IDENTIFIER, "Expected variable name.")
        initializer = None
        if self.match(TokenType.EQUAL):
            initializer = self.expression()
        self.consume(TokenType.SEMICOLON, "Expected ';' after variable declaration.")
        return Var(name, initializer)

    #parses statement, currently print statements only
    def statement(self) -> Stmt:
        if self.match(TokenType.PRINT):
            return self.print_statement()
        return self.expression_statement()

    #parse body of print statement, calls expression() for value, then checks for semicolon
    def print_statement(self) -> Stmt:
        value = self.expression()
        self.consume(TokenType.SEMICOLON, "Expected ';' after value.")
        return Print(value)

    def expression_statement(self) -> Stmt:
        expr = self.expression()
        self.consume(TokenType.SEMICOLON, "Expected ';' after expression.")
        return Expression(expr)

    #parses expression, string literals rn
    def expression(self):
        return self.assignment()

    def assignment(self):
        expr = self.or_expression()

        if self.match(TokenType.EQUAL):
            equals = self.previous()
            value = self.assignment()

            if isinstance(expr, Variable):
                return Assign(expr.name, value)

            error(equals.line, equals, "Invalid assignment target.")
            raise ParseErr()

        return expr

    def or_expression(self):
        expr = self.and_expression()

        while self.match(TokenType.OR):
            operator = self.previous()
            right = self.and_expression()
            expr = Logical(expr, operator, right)

        return expr

    def and_expression(self):
        expr = self.equality()

        while self.match(TokenType.AND):
            operator = self.previous()
            right = self.equality()
            expr = Logical(expr, operator, right)

        return expr

    def equality(self):
        expr = self.comparison()

        while self.match(TokenType.BANG_EQUAL, TokenType.EQUAL_EQUAL):
            operator = self.previous()
            right = self.comparison()
            expr = Binary(expr, operator, right)

        return expr

    def comparison(self):
        expr = self.term()

        while self.match(TokenType.GREATER, TokenType.GREATER_EQUAL, TokenType.LESS, TokenType.LESS_EQUAL):
            operator = self.previous()
            right = self.term()
            expr = Binary(expr, operator, right)

        return expr

    def term(self):
        expr = self.factor()

        while self.match(TokenType.PLUS, TokenType.MINUS):
            operator = self.previous()
            right = self.factor()
            expr = Binary(expr, operator, right)

        return expr

    def factor(self):
        expr = self.unary()

        while self.match(TokenType.STAR, TokenType.SLASH):
            operator = self.previous()
            right = self.unary()
            expr = Binary(expr, operator, right)

        return expr

    def unary(self):
        if self.match(TokenType.BANG, TokenType.MINUS):
            operator = self.previous()
            right = self.unary()
            return Unary(operator, right)

        return self.primary()

    def primary(self):
        if self.match(TokenType.TRUE):
            return Literal(True)

        if self.match(TokenType.FALSE):
            return Literal(False)

        if self.match(TokenType.NIL):
            return Literal(None)

        if self.match(TokenType.IDENTIFIER):
            return Variable(self.previous())

        if self.match(TokenType.LEFT_PAREN):
            expr = self.expression()
            self.consume(TokenType.RIGHT_PAREN, "Expected ')' after expression.")
            return Grouping(expr)

        if self.match(TokenType.STRING, TokenType.NUMBER):
            return Literal(self.previous().literal)

        tok = self.peek()
        error(tok.line, tok, "Expected expression.")
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
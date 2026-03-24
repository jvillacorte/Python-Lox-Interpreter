from token_type import TokenType
from expressions import Assign, Binary, Call, Grouping, Literal, Logical, Unary, Variable
from statements import Block, Expression, Function, If, Print, Return, Stmt, Var, While
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
            stmt = self.declaration()
            if stmt is not None:
                stmts.append(stmt)
        return stmts

    def declaration(self) -> Stmt | None:
        try:
            if self.match(TokenType.FUN):
                return self.function("function")
            if self.match(TokenType.VAR):
                return self.var_declaration()
            return self.statement()
        except ParseErr:
            self.synchronize()
            return None

    def function(self, kind: str) -> Function:
        name = self.consume(TokenType.IDENTIFIER, f"Expected {kind} name.")
        self.consume(TokenType.LEFT_PAREN, f"Expected '(' after {kind} name.")

        parameters: list = []
        if not self.check(TokenType.RIGHT_PAREN):
            while True:
                if len(parameters) >= 255:
                    tok = self.peek()
                    error(token=tok, msg="Cannot have more than 255 parameters.")
                    raise ParseErr()
                parameters.append(self.consume(TokenType.IDENTIFIER, "Expected parameter name."))
                if not self.match(TokenType.COMMA):
                    break

        self.consume(TokenType.RIGHT_PAREN, "Expected ')' after parameters.")
        self.consume(TokenType.LEFT_BRACE, f"Expected '{{' before {kind} body.")
        body = self.block()
        return Function(name, parameters, body)

    def var_declaration(self) -> Stmt:
        name = self.consume(TokenType.IDENTIFIER, "Expected variable name.")
        initializer = None
        if self.match(TokenType.EQUAL):
            initializer = self.expression()
        self.consume(TokenType.SEMICOLON, "Expected ';' after variable declaration.")
        return Var(name, initializer)

    #parses statements, checks for statement type by looking at first token
    #then calls appropriate parsing function
    def statement(self) -> Stmt:
        if self.match(TokenType.FOR):
            return self.for_statement()
        if self.match(TokenType.IF):
            return self.if_statement()
        if self.match(TokenType.WHILE):
            return self.while_statement()
        if self.match(TokenType.PRINT):
            return self.print_statement()
        if self.match(TokenType.RETURN):
            return self.return_statement()
        if self.match(TokenType.LEFT_BRACE):
            return Block(self.block())
        return self.expression_statement()

    def for_statement(self) -> Stmt:
        self.consume(TokenType.LEFT_PAREN, "Expected '(' after 'for'.")

        initializer = None
        if self.match(TokenType.SEMICOLON):
            pass
        elif self.match(TokenType.VAR):
            initializer = self.var_declaration()
        else:
            initializer = self.expression_statement()

        condition = None
        if not self.check(TokenType.SEMICOLON):
            condition = self.expression()
        self.consume(TokenType.SEMICOLON, "Expected ';' after loop condition.")

        increment = None
        if not self.check(TokenType.RIGHT_PAREN):
            increment = self.expression()
        self.consume(TokenType.RIGHT_PAREN, "Expected ')' after for clauses.")

        body = self.statement()

        if increment is not None:
            body = Block([body, Expression(increment)])

        if condition is None:
            condition = Literal(True)
        body = While(condition, body)

        if initializer is not None:
            body = Block([initializer, body])

        return body

    def if_statement(self) -> Stmt:
        self.consume(TokenType.LEFT_PAREN, "Expected '(' after 'if'.")
        condition = self.expression()
        self.consume(TokenType.RIGHT_PAREN, "Expected ')' after if condition.")

        then_branch = self.statement()
        else_branch = None
        if self.match(TokenType.ELSE):
            else_branch = self.statement()

        return If(condition, then_branch, else_branch)

    def while_statement(self) -> Stmt:
        self.consume(TokenType.LEFT_PAREN, "Expected '(' after 'while'.")
        condition = self.expression()
        self.consume(TokenType.RIGHT_PAREN, "Expected ')' after condition.")
        body = self.statement()
        return While(condition, body)

    def return_statement(self) -> Stmt:
        keyword = self.previous()
        value = None
        if not self.check(TokenType.SEMICOLON):
            value = self.expression()

        self.consume(TokenType.SEMICOLON, "Expected ';' after return value.")
        return Return(keyword, value)

    #parse body of print statement, calls expression() for value, then checks for semicolon
    def print_statement(self) -> Stmt:
        value = self.expression()
        self.consume(TokenType.SEMICOLON, "Expected ';' after value.")
        return Print(value)

    def expression_statement(self) -> Stmt:
        expr = self.expression()
        self.consume(TokenType.SEMICOLON, "Expected ';' after expression.")
        return Expression(expr)

    def block(self) -> list[Stmt]:
        statements: list[Stmt] = []

        while not self.check(TokenType.RIGHT_BRACE) and not self.tok_end():
            stmt = self.declaration()
            if stmt is not None:
                statements.append(stmt)

        self.consume(TokenType.RIGHT_BRACE, "Expected '}' after block.")
        return statements

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

            error(token=equals, msg="Invalid assignment target.")
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

        return self.call()

    def call(self):
        expr = self.primary()

        while True:
            if self.match(TokenType.LEFT_PAREN):
                expr = self.finish_call(expr)
            else:
                break

        return expr

    def finish_call(self, callee):
        arguments: list = []
        if not self.check(TokenType.RIGHT_PAREN):
            while True:
                if len(arguments) >= 255:
                    tok = self.peek()
                    error(token=tok, msg="Cannot have more than 255 arguments.")
                    raise ParseErr()
                arguments.append(self.expression())
                if not self.match(TokenType.COMMA):
                    break

        paren = self.consume(TokenType.RIGHT_PAREN, "Expected ')' after arguments.")
        return Call(callee, paren, arguments)

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
        error(token=tok, msg="Expected expression.")
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
        error(token=tok, msg=msg)
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

    def synchronize(self) -> None:
        self.advance()

        while not self.tok_end():
            if self.previous().type == TokenType.SEMICOLON:
                return

            if self.peek().type in (
                TokenType.FUN,
                TokenType.VAR,
                TokenType.FOR,
                TokenType.IF,
                TokenType.WHILE,
                TokenType.PRINT,
                TokenType.RETURN,
            ):
                return

            self.advance()
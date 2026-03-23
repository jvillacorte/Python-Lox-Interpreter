from visitor import Visitor
from expressions import Assign, Binary, Grouping, Literal, Logical, Unary, Variable
from statements import Expression, Print, Var
from token_type import TokenType
from error import RuntimeErr, error


class Environment:
    def __init__(self) -> None:
        self.values: dict[str, object] = {}

    def define(self, name: str, value: object) -> None:
        self.values[name] = value

    def get(self, name_token) -> object:
        if name_token.lexeme in self.values:
            return self.values[name_token.lexeme]
        raise RuntimeErr(name_token, f"Undefined variable '{name_token.lexeme}'.")

    def assign(self, name_token, value: object) -> None:
        if name_token.lexeme in self.values:
            self.values[name_token.lexeme] = value
            return
        raise RuntimeErr(name_token, f"Undefined variable '{name_token.lexeme}'.")


class Interpreter(Visitor):
    def __init__(self) -> None:
        self.environment = Environment()

    def interpret(self, statements) -> None:
        try:
            for stmt in statements:
                stmt.accept(self)
        except RuntimeErr as err:
            error(err.token.line, err.token, err.message)

    def visit_print_stmt(self, stmt: Print) -> None:
        value = stmt.expression.accept(self)
        print(self.stringify(value))

    def visit_binary_expr(self, expr: Binary) -> object:
        left = expr.left.accept(self)
        right = expr.right.accept(self)

        # Comparison operators
        if expr.operator.type in (TokenType.GREATER, TokenType.GREATER_EQUAL, TokenType.LESS, TokenType.LESS_EQUAL):
            if not isinstance(left, float) or not isinstance(right, float):
                raise RuntimeErr(expr.operator, "Operands for comparison must be numbers.")
            if expr.operator.type == TokenType.GREATER:
                return left > right
            if expr.operator.type == TokenType.GREATER_EQUAL:
                return left >= right
            if expr.operator.type == TokenType.LESS:
                return left < right
            if expr.operator.type == TokenType.LESS_EQUAL:
                return left <= right

        # Equality operators
        if expr.operator.type == TokenType.EQUAL_EQUAL:
            return self.is_equal(left, right)
        if expr.operator.type == TokenType.BANG_EQUAL:
            return not self.is_equal(left, right)

        # Arithmetic operators
        if not isinstance(left, float) or not isinstance(right, float):
            raise RuntimeErr(expr.operator, "Operands for '+', '-', '*', and '/' must be numbers.")

        if expr.operator.type == TokenType.PLUS:
            return left + right
        if expr.operator.type == TokenType.MINUS:
            return left - right
        if expr.operator.type == TokenType.STAR:
            return left * right
        if expr.operator.type == TokenType.SLASH:
            if right == 0.0:
                raise RuntimeErr(expr.operator, "Division by zero.")
            return left / right

        raise RuntimeErr(expr.operator, "Unknown binary operator.")

    def visit_grouping_expr(self, expr: Grouping) -> object:
        return expr.expression.accept(self)

    def visit_literal_expr(self, expr: Literal) -> object:
        return expr.value

    def visit_logical_expr(self, expr: Logical) -> object:
        left = expr.left.accept(self)

        if expr.operator.type == TokenType.OR:
            if self.is_truthy(left):
                return left
        else:  # AND
            if not self.is_truthy(left):
                return left

        return expr.right.accept(self)

    def visit_unary_expr(self, expr: Unary) -> object:
        right = expr.right.accept(self)

        if expr.operator.type == TokenType.BANG:
            return not self.is_truthy(right)
        if expr.operator.type == TokenType.MINUS:
            if not isinstance(right, float):
                raise RuntimeErr(expr.operator, "Operand for unary '-' must be a number.")
            return -right

        raise RuntimeErr(expr.operator, "Unknown unary operator.")

    def visit_variable_expr(self, expr: Variable) -> object:
        return self.environment.get(expr.name)

    def visit_assign_expr(self, expr: Assign) -> object:
        value = expr.value.accept(self)
        self.environment.assign(expr.name, value)
        return value

    def visit_var_stmt(self, stmt: Var) -> object:
        value = None
        if stmt.initializer is not None:
            value = stmt.initializer.accept(self)
        self.environment.define(stmt.name.lexeme, value)
        return None

    def visit_expression_stmt(self, stmt: Expression) -> object:
        stmt.expression.accept(self)
        return None

    def is_truthy(self, value: object) -> bool:
        if value is None or value is False:
            return False
        return True

    def is_equal(self, left: object, right: object) -> bool:
        if type(left) != type(right):
            return False
        return left == right

    def stringify(self, value: object) -> str:
        if isinstance(value, bool):
            return "true" if value else "false"
        if isinstance(value, float):
            text = str(value)
            if text.endswith(".0"):
                return text[:-2]
            return text
        if value is None:
            return ""
        return str(value)
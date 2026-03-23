from visitor import Visitor
from expressions import Binary, Grouping, Literal
from statements import Print
from token_type import TokenType
from error import RuntimeErr, error


class Interpreter(Visitor):
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

    def stringify(self, value: object) -> str:
        if isinstance(value, float):
            text = str(value)
            if text.endswith(".0"):
                return text[:-2]
            return text
        return str(value)
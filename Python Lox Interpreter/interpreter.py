from visitor import Visitor
from expressions import Literal
from statements import Print


class Interpreter(Visitor):
    def interpret(self, statements) -> None:
        for stmt in statements:
            stmt.accept(self)

    def visit_print_stmt(self, stmt: Print) -> None:
        value = stmt.expression.accept(self)
        print(value)

    def visit_literal_expr(self, expr: Literal) -> object:
        return expr.value
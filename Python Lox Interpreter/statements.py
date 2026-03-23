from abc import ABC, abstractmethod
from expressions import Expor

class Stmt(ABC):
    @abstractmethod
    def accept(self, visitor):
        raise NotImplementedError
    
class Print(Stmt):
    def __init__(self, expression: Expor) -> None:
        self.expression = expression
    
    def accept(self, visitor):
        return visitor.visit_print_stmt(self)


class Expression(Stmt):
    def __init__(self, expression: Expor) -> None:
        self.expression = expression

    def accept(self, visitor):
        return visitor.visit_expression_stmt(self)


class Var(Stmt):
    def __init__(self, name, initializer: Expor | None) -> None:
        self.name = name
        self.initializer = initializer

    def accept(self, visitor):
        return visitor.visit_var_stmt(self)
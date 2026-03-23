from abc import ABC, abstractmethod
from expressions import Binary, Grouping, Literal
from statements import Print

class Visitor(ABC):
    @abstractmethod
    def visit_binary_expr(self, expr: Binary) -> object:
        raise NotImplementedError

    @abstractmethod
    def visit_grouping_expr(self, expr: Grouping) -> object:
        raise NotImplementedError

    @abstractmethod
    def visit_literal_expr(self, expr: Literal) -> object:
        raise NotImplementedError
    
    @abstractmethod
    def visit_print_stmt(self, stmt: Print) -> object:
        raise NotImplementedError
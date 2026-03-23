from abc import ABC, abstractmethod
from expressions import Assign, Binary, Grouping, Literal, Logical, Unary, Variable
from statements import Expression, Print, Var

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
    def visit_logical_expr(self, expr: Logical) -> object:
        raise NotImplementedError

    @abstractmethod
    def visit_unary_expr(self, expr: Unary) -> object:
        raise NotImplementedError

    @abstractmethod
    def visit_variable_expr(self, expr: Variable) -> object:
        raise NotImplementedError

    @abstractmethod
    def visit_assign_expr(self, expr: Assign) -> object:
        raise NotImplementedError
    
    @abstractmethod
    def visit_print_stmt(self, stmt: Print) -> object:
        raise NotImplementedError

    @abstractmethod
    def visit_var_stmt(self, stmt: Var) -> object:
        raise NotImplementedError

    @abstractmethod
    def visit_expression_stmt(self, stmt: Expression) -> object:
        raise NotImplementedError
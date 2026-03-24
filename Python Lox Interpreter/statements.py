from abc import ABC, abstractmethod
from expressions import Expor
from token_cls import Token

#base class for statement nodes, defines visitor pattern
class Stmt(ABC):
    @abstractmethod
    def accept(self, visitor):
        raise NotImplementedError
    
#print expression to console
class Print(Stmt):
    def __init__(self, expression: Expor) -> None:
        self.expression = expression
    
    def accept(self, visitor):
        return visitor.visit_print_stmt(self)

#expression statement such as a=2; or add(1,2);
class Expression(Stmt):
    def __init__(self, expression: Expor) -> None:
        self.expression = expression

    def accept(self, visitor):
        return visitor.visit_expression_stmt(self)


#variable declaration var x;
class Var(Stmt):
    def __init__(self, name, initializer: Expor | None) -> None:
        self.name = name
        self.initializer = initializer

    def accept(self, visitor):
        return visitor.visit_var_stmt(self)

#curly brace statement block, executes in nested scope
class Block(Stmt):
    def __init__(self, statements: list[Stmt]) -> None:
        self.statements = statements

    def accept(self, visitor):
        return visitor.visit_block_stmt(self)


#if condition then_branch else_branch, where else branch can be none
#evaluates condition truth, executes branch if true, else branch if false
class If(Stmt):
    def __init__(self, condition: Expor, then_branch: Stmt, else_branch: Stmt | None) -> None:
        self.condition = condition
        self.then_branch = then_branch
        self.else_branch = else_branch

    def accept(self, visitor):
        return visitor.visit_if_stmt(self)

#while condition, body, evaluates truth of condition, executes if true, then
#continues to evaluate and execute body until condition is false
class While(Stmt):
    def __init__(self, condition: Expor, body: Stmt) -> None:
        self.condition = condition
        self.body = body

    def accept(self, visitor):
        return visitor.visit_while_stmt(self)

#function name, parameters, and body implementation
class Function(Stmt):
    def __init__(self, name: Token, params: list[Token], body: list[Stmt]) -> None:
        self.name = name
        self.params = params
        self.body = body

    def accept(self, visitor):
        return visitor.visit_function_stmt(self)

#returns from function, with optional return value
class Return(Stmt):
    def __init__(self, keyword: Token, value: Expor | None) -> None:
        self.keyword = keyword
        self.value = value

    def accept(self, visitor):
        return visitor.visit_return_stmt(self)
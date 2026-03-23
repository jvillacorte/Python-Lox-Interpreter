from abc import ABC, abstractmethod
from token_cls import Token

#base class for  expressions, defines visitor pattern
class Expor(ABC):
    @abstractmethod
    def accept(self, visitor):
        raise NotImplementedError
    
#Constant values, like numbers, strings, and true false
class Literal(Expor):
    def __init__(self, value: object) -> None:
        self.value = value
    
    def accept(self, visitor):
        return visitor.visit_literal_expr(self)

#plus minus, etc
class Binary(Expor):
    def __init__(self, left: Expor, operator: Token, right: Expor) -> None:
        self.left = left
        self.operator = operator
        self.right = right

    def accept(self, visitor):
        return visitor.visit_binary_expr(self)

#parenthesized expressions, ex. (1+2)
class Grouping(Expor):
    def __init__(self, expression: Expor) -> None:
        self.expression = expression

    def accept(self, visitor):
        return visitor.visit_grouping_expr(self)


#Logical operators, and/or
class Logical(Expor):
    def __init__(self, left: Expor, operator: Token, right: Expor) -> None:
        self.left = left
        self.operator = operator
        self.right = right

    def accept(self, visitor):
        return visitor.visit_logical_expr(self)

#unary like !true, or -1
class Unary(Expor):
    def __init__(self, operator: Token, right: Expor) -> None:
        self.operator = operator
        self.right = right

    def accept(self, visitor):
        return visitor.visit_unary_expr(self)


class Variable(Expor):
    def __init__(self, name: Token) -> None:
        self.name = name

    def accept(self, visitor):
        return visitor.visit_variable_expr(self)


class Assign(Expor):
    def __init__(self, name: Token, value: Expor) -> None:
        self.name = name
        self.value = value

    def accept(self, visitor):
        return visitor.visit_assign_expr(self)
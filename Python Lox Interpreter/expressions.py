from abc import ABC, abstractmethod
from token_cls import Token

class Expor(ABC):
    @abstractmethod
    def accept(self, visitor):
        raise NotImplementedError
    
class Literal(Expor):
    def __init__(self, value: object) -> None:
        self.value = value
    
    def accept(self, visitor):
        return visitor.visit_literal_expr(self)


class Binary(Expor):
    def __init__(self, left: Expor, operator: Token, right: Expor) -> None:
        self.left = left
        self.operator = operator
        self.right = right

    def accept(self, visitor):
        return visitor.visit_binary_expr(self)


class Grouping(Expor):
    def __init__(self, expression: Expor) -> None:
        self.expression = expression

    def accept(self, visitor):
        return visitor.visit_grouping_expr(self)
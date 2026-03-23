from abc import ABC, abstractmethod

class Expor(ABC):
    @abstractmethod
    def accept(self, visitor):
        raise NotImplementedError
    
class Literal(Expor):
    def __init__(self, value: object) -> None:
        self.value = value
    
    def accept(self, visitor):
        return visitor.visit_literal_expr(self)
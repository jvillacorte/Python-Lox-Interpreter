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
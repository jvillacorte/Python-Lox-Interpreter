from visitor import Visitor
from expressions import Assign, Binary, Call, Grouping, Literal, Logical, Unary, Variable
from statements import Block, Expression, Function, If, Print, Return, Var, While
from token_type import TokenType
from error import RuntimeErr, error


class Environment:
    #storage map for variables
    def __init__(self, enclosing=None) -> None:
        self.values: dict[str, object] = {}
        self.enclosing = enclosing

    #define new variable in environment with name and value
    def define(self, name: str, value: object) -> None:
        self.values[name] = value

    #get value of variable from environment if variable exists, else returns error
    def get(self, name_token) -> object:
        if name_token.lexeme in self.values:
            return self.values[name_token.lexeme]
        if self.enclosing is not None:
            return self.enclosing.get(name_token)
        raise RuntimeErr(name_token, f"Undefined variable '{name_token.lexeme}'.")

    #update value of existing variable in environment, else returns error
    def assign(self, name_token, value: object) -> None:
        if name_token.lexeme in self.values:
            self.values[name_token.lexeme] = value
            return
        if self.enclosing is not None:
            self.enclosing.assign(name_token, value)
            return
        raise RuntimeErr(name_token, f"Undefined variable '{name_token.lexeme}'.")


class LoxCallable:
    def arity(self) -> int:
        raise NotImplementedError

    def call(self, interpreter, arguments: list[object]) -> object:
        raise NotImplementedError


class ReturnSignal(Exception):
    def __init__(self, value: object) -> None:
        self.value = value


class LoxFunction(LoxCallable):
    def __init__(self, declaration: Function, closure: Environment) -> None:
        self.declaration = declaration
        self.closure = closure

    def arity(self) -> int:
        return len(self.declaration.params)

    def call(self, interpreter, arguments: list[object]) -> object:
        environment = Environment(self.closure)
        for i, param in enumerate(self.declaration.params):
            environment.define(param.lexeme, arguments[i])

        interpreter.function_depth += 1
        try:
            interpreter.execute_block(self.declaration.body, environment)
        except ReturnSignal as signal:
            return signal.value
        finally:
            interpreter.function_depth -= 1

        return None

    def __str__(self) -> str:
        return f"<fn {self.declaration.name.lexeme}>"


class Interpreter(Visitor):
    #create interpreter with environment instance
    def __init__(self) -> None:
        self.environment = Environment()
        self.function_depth = 0

    #iterate through parsed statements, executing each, except runtime errors, which are caught and throw an error message
    def interpret(self, statements) -> None:
        try:
            for stmt in statements:
                stmt.accept(self)
        except RuntimeErr as err:
            error(err.token.line, err.token, err.message)

    def execute_block(self, statements: list, environment: Environment) -> None:
        previous = self.environment
        try:
            self.environment = environment
            for stmt in statements:
                stmt.accept(self)
        finally:
            self.environment = previous

    #execute print statement, evaluate expression, convecrt to user-facing string and print to console
    def visit_print_stmt(self, stmt: Print) -> None:
        value = stmt.expression.accept(self)
        print(self.stringify(value))

    #evaluates binary operators with three groups
    #comparison, equality, and arithmetic
    #left and right comparisons such as greater/less than
    #equality comparisons == and !=
    #arithmetic comparisosn, plus, minus, etc, checks for division by zero which throws unique error
    def visit_binary_expr(self, expr: Binary) -> object:
        left = expr.left.accept(self)
        right = expr.right.accept(self)

        # Comparison operators
        if expr.operator.type in (TokenType.GREATER, TokenType.GREATER_EQUAL, TokenType.LESS, TokenType.LESS_EQUAL):
            if not isinstance(left, float) or not isinstance(right, float):
                raise RuntimeErr(expr.operator, "Operands for comparison must be numbers.")
            if expr.operator.type == TokenType.GREATER:
                return left > right
            if expr.operator.type == TokenType.GREATER_EQUAL:
                return left >= right
            if expr.operator.type == TokenType.LESS:
                return left < right
            if expr.operator.type == TokenType.LESS_EQUAL:
                return left <= right

        # Equality operators
        if expr.operator.type == TokenType.EQUAL_EQUAL:
            return self.is_equal(left, right)
        if expr.operator.type == TokenType.BANG_EQUAL:
            return not self.is_equal(left, right)

        # Arithmetic operators
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

    #parenthesized expressions handling, evaluates inner expression directly
    def visit_grouping_expr(self, expr: Grouping) -> object:
        return expr.expression.accept(self)

    #returns literal value as-is, such as true/false/bool/string/num
    def visit_literal_expr(self, expr: Literal) -> object:
        return expr.value

    #short circuit logic
    #if left operand of OR is truthy, return left else evaluate and return right
    #if left operand of AND is falsy, return left, else evaluate and return right
    def visit_logical_expr(self, expr: Logical) -> object:
        left = expr.left.accept(self)

        if expr.operator.type == TokenType.OR:
            if self.is_truthy(left):
                return left
        else:  # AND
            if not self.is_truthy(left):
                return left

        return expr.right.accept(self)

    #unary operators, not and minus, checks type erorrs
    def visit_unary_expr(self, expr: Unary) -> object:
        right = expr.right.accept(self)

        if expr.operator.type == TokenType.BANG:
            return not self.is_truthy(right)
        if expr.operator.type == TokenType.MINUS:
            if not isinstance(right, float):
                raise RuntimeErr(expr.operator, "Operand for unary '-' must be a number.")
            return -right

        raise RuntimeErr(expr.operator, "Unknown unary operator.")

    #looks up variable token in current environment, returns stored value else throwing an error
    def visit_variable_expr(self, expr: Variable) -> object:
        return self.environment.get(expr.name)

    #evaluates right hand value, write into environment with variable name, returns value
    def visit_assign_expr(self, expr: Assign) -> object:
        value = expr.value.accept(self)
        self.environment.assign(expr.name, value)
        return value

    def visit_call_expr(self, expr: Call) -> object:
        callee = expr.callee.accept(self)
        arguments = [argument.accept(self) for argument in expr.arguments]

        if not isinstance(callee, LoxCallable):
            raise RuntimeErr(expr.paren, "Can only call functions.")

        if len(arguments) != callee.arity():
            raise RuntimeErr(
                expr.paren,
                f"Expected {callee.arity()} arguments but got {len(arguments)}.",
            )

        return callee.call(self, arguments)

    #variable declaration in statement, default nil value if nothing initialized
    def visit_var_stmt(self, stmt: Var) -> object:
        value = None
        if stmt.initializer is not None:
            value = stmt.initializer.accept(self)
        self.environment.define(stmt.name.lexeme, value)
        return None

    #executes expression statements, where result is not printed
    #evaluates and discards value
    def visit_expression_stmt(self, stmt: Expression) -> object:
        stmt.expression.accept(self)
        return None

    #executes block statements, creates new environment for block with 
    # enclosing environment as current environment, executes block statements in new environment, then restores previous environment
    def visit_block_stmt(self, stmt: Block) -> object:
        self.execute_block(stmt.statements, Environment(self.environment))
        return None

    #evaluates if statement executes then branch if condition is truthy
    #else executes else branch if condition is falsy and else branch exists, else does nothing
    def visit_if_stmt(self, stmt: If) -> object:
        if self.is_truthy(stmt.condition.accept(self)):
            stmt.then_branch.accept(self)
        elif stmt.else_branch is not None:
            stmt.else_branch.accept(self)
        return None

    #evaluates loop conditions, continues to execute while condition is truthy, else exits loop
    def visit_while_stmt(self, stmt: While) -> object:
        while self.is_truthy(stmt.condition.accept(self)):
            stmt.body.accept(self)
        return None

    def visit_function_stmt(self, stmt: Function) -> object:
        function = LoxFunction(stmt, self.environment)
        self.environment.define(stmt.name.lexeme, function)
        return None

    #prevents returning from top-level code, evaluates return value if exists
    def visit_return_stmt(self, stmt: Return) -> object:
        if self.function_depth == 0:
            raise RuntimeErr(stmt.keyword, "Cannot return from top-level code.")

        value = None
        if stmt.value is not None:
            value = stmt.value.accept(self)
        raise ReturnSignal(value)

    #false and false = false, everything else true
    def is_truthy(self, value: object) -> bool:
        if value is None or value is False:
            return False
        return True

    #checks for same type and value for equality, if different type returns false, else evaluates equality
    def is_equal(self, left: object, right: object) -> bool:
        if type(left) != type(right):
            return False
        return left == right

    #convert runtime values to user-facing strings, such as true/false/nil
    def stringify(self, value: object) -> str:
        if isinstance(value, bool):
            return "true" if value else "false"
        if isinstance(value, float):
            text = str(value)
            if text.endswith(".0"):
                return text[:-2]
            return text
        if value is None:
            return "nil"
        return str(value)
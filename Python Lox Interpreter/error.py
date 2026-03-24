from sys import stderr

had_err = False

class RuntimeErr(Exception):
    def __init__(self, token, message: str) -> None:
        self.token = token
        self.message = message
        super().__init__(self.message)


class ParseErr(Exception):
    pass

def set_err_status(value: bool) -> None:
    global had_err
    had_err = value

def get_err_status() -> bool:
    return had_err

def report(line: int, where: str, message: str) -> None:
    print(f'[line {line}] Error{where}: {message}', file=stderr)
    set_err_status(True)

def error(line: int | None = None, token=None, msg: str = "Error") -> None:
    if token is not None:
        report(token.line, f" at '{token.lexeme}'", msg)
        return

    if line is None:
        line = 0
    report(line, "", msg)
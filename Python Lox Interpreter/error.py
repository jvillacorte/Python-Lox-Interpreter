from sys import stderr

had_err = False

#runtime failures when executing code
#stores tiken where runtime problem happened and message describing error
class RuntimeErr(Exception):
    def __init__(self, token, message: str) -> None:
        self.token = token
        self.message = message
        super().__init__(self.message)

#parsing failures when parsing code
#dont do nothing
class ParseErr(Exception):
    pass

#reports error to stderr, sets error status to true, used for both runtime and parse errors
def set_err_status(value: bool) -> None:
    global had_err
    had_err = value

#reads global had_err flag, checks if error has occured after scan/parse/interpret stages to determine if program should exit with error code
def get_err_status() -> bool:
    return had_err

#reports error to stderr, sets error status to true, used for both runtime and parse errors
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
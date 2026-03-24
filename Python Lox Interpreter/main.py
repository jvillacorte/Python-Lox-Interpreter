#!/usr/bin/env python3

from sys import argv, exit
from error import get_err_status
from scanner import Scanner
from token_parser import Parser
from interpreter import Interpreter


#runs one script, exits with error code if error occurs
#if valid call run_script with path to script as argument
def main() -> None:
    if len(argv) != 2:
        print("Usage: python main.py <script>")
        exit(64)

    run_script(argv[1])

#read source file
#scan text into tokens
#stop if there's errors
#parse tokens into statements
#stops if there's errors
#interpret AST
#stop if runtime error occurs
#runs main when executed directly, not imported as module
def run_script(path: str) -> None:
    with open(path, "r", encoding="utf-8") as f:
        source = f.read()

    scanner = Scanner(source)
    tokens = scanner.scan_tokens()

    if get_err_status():
        exit(65)

    parser = Parser(tokens)
    statements = parser.parse()

    if get_err_status():
        exit(65)

    interpreter = Interpreter()
    interpreter.interpret(statements)

    if get_err_status():
        exit(70)


if __name__ == "__main__":
    main()
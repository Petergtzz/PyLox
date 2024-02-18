# pylox.py
# 
# Main program

from error_handler import ErrorHandler
from interpreter import Interpreter
from parse import Parser
from scanner import Scanner

class PyLox:
    '''
    Base class for the dinamically-typed language PyLox. 

    Attributes
    ----------
    interpreter : class
        traverses through the syntax tree
    error_handler : class
        reports errors
    '''
    def __init__(self):
        self.interpreter = Interpreter()
        self.error_handler = ErrorHandler()

    def run_file(self, source):
        with open(source) as file:
            lines = file.read()
        self.run(lines)

        if self.error_handler.had_error or self.error_handler.had_runtime_error:
            raise SystemExit
        
    def run_promt(self):
        while True:
            try: 
                source = input('> ')
                self.run(source)
                self.error_handler.had_error = False
            except EOFError:
                pass

    def run(self, source):
        scanner = Scanner(source, self.error_handler)
        tokens = scanner.scan_tokens()
        
        parser = Parser(tokens, self.error_handler)
        statements = parser.parse()

        if self.error_handler.had_error:
            return
    
        self.interpreter.interpret(statements)
        
def main(argv):
    program = PyLox()
    if len(argv) > 2:
        raise SystemExit('Usage: pylox filename')
    elif len(argv) == 2:
        program.run_file(argv[1])
    else:
        program.run_promt()

if __name__ == '__main__':
    import sys
    main(sys.argv)    
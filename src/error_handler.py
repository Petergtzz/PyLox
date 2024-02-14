# error_handler.py

from tokens import Token
from token_type import TokenType

class ErrorHandler(Exception):
    '''
    This class helps tell the user some syntax error occured and report it

    Attributes
    ----------
    had_error : bool
        to ensure code is not executed that has known error
    had_runtime_error : bool
        ...
        
    '''
    def __init__(self):
        self.had_error = False
        self.had_runtime_error = False

    def error(self, token, message):
        if isinstance(token, Token):
            if token.type == TokenType.EOF:
                self.report(token.line, "", message)
            else: 
                self.report(token.line,  " at '" + token.lexeme + "'", message)
        else:
            self.report(token, '', message)

    def runtime_error(self, error):
        print(f'{error.message}\n[line {error.token.line}]')
        self.had_runtime_error = True
    
    def report(self, line, where, message):
        print(f'[line {line}] Error {where}: {message}')
        self.had_error = True

    

        
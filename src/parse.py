
# parse.py

from token_type import TokenType
from expr import *

class ParseError(Exception):
    pass

class Parser: 
    _tokens = []
    _current = 0

    def __init__(self, tokens, error_handler):
        self.error_handler = error_handler
        self._tokens = tokens

    def parse(self):
        statements = list()
        while not self.is_at_end():
            statements.append(self.statement())

        return statements

    #def parse(self):
    #    try:
    #        return self.expression()
    #    except ParseError as error:
    #        return None

    def expression(self):
        return self.equality()
    
    def declaration(self):
        try:
            if self.match(TokenType.VAR):
                return self.var_declaration()
            else: 
                return self.statement()
        except ParseError() as error: 
            self.synchronize()
            return None
        
    def statement(self):
        if self.match(TokenType.PRINT):
            return self.print_statement()
        return self.expression_statement()
    
    def print_statement(self):
        value = self.expression()
        self.consume(TokenType.SEMICOLON, "Expect ';' after value.")
        return Print(value)
    
    def var_declaration(self):
        name = self.consume(TokenType.IDENTIFIER, "Expect variable name.")

        identifier = None
        if self.match(TokenType.EQUAL):
            identifier = self.expression()

        self.consume(TokenType.SEMICOLON, "Expect ';' after variable declaration")
        return VarDeclaration(name, identifier)
    
    def expression_statement(self):
        value = self.expression()
        self.consume(TokenType.SEMICOLON, "Expect ';' after expression.")
        return ExprStmt(value)
    
    def equality(self):
        expr = self.comparison()
        
        while self.match(TokenType.BANG_EQUAL, TokenType.EQUAL_EQUAL):
            operator = self.previous()
            right = self.comparison()
            expr = Binary(expr, operator, right)
        
        return expr
    
    def comparison(self):
        expr = self.term()

        while self.match(TokenType.GREATER, TokenType.GREATER_EQUAL, TokenType.LESS, TokenType.LESS_EQUAL):
            operator = self.previous()
            right = self.term()
            expr = Binary(expr, operator, right)

        return expr
    
    def term(self):
        expr = self.factor()

        while self.match(TokenType.MINUS, TokenType.PLUS):
            operator = self.previous()
            right = self.factor()
            expr = Binary(expr, operator, right)

        return expr
    
    def factor(self):
        expr = self.unary()

        while self.match(TokenType.SLASH, TokenType.STAR):
            operator = self.previous()
            right = self.unary()
            expr = Binary(expr, operator, right)

        return expr
    
    def unary(self):
        if self.match(TokenType.BANG, TokenType.MINUS):
            operator = self.previous()
            right = self.unary()
            return Unary(operator, right)

        return self.primary()
    
    def primary(self):
        if self.match(TokenType.FALSE):
            return Literal(False)
        elif self.match(TokenType.TRUE):
            return Literal(True)
        elif self.match(TokenType.NIL):
            return Literal(None)
        elif self.match(TokenType.NUMBER, TokenType.STRING):
            return Literal(self.previous().literal)

        if self.match(TokenType.IDENTIFIER):
            return Variable(self.previous()) 
        
        if self.match(TokenType.LEFT_PAREN):
            expr = self.expression()
            self.consume(TokenType.RIGHT_PAREN, "Expect ')' after expression.")
            return Grouping(expr)
        
        self.error(self.peek(), 'Expect expression.')
    
    def match(self, *types):
        for type in types: 
            if self.check(type):
                self.advance()
                return True
        
        return False
    
    def consume(self, type, message):
        if self.match(type):
            return self.advance()
        else: 
            self.error(self.peek(), message)
    
    def check(self, type):
        if self.is_at_end():
            return False
        return self.peek().type == type
        
    def advance(self):
        if not self.is_at_end():
            self._current += 1
        return self.previous()
    
    def is_at_end(self):
        return self.peek().type == TokenType.EOF

    def peek(self):
        return self._tokens[self._current]

    def previous(self):
        return self._tokens[self._current - 1]
    
    def error(self, token, message):
        self.error_handler.error(token, message)
        return ParseError()
    
    def synchronize(self):
        self.advance()

        while not self.is_at_end():
            if self.previous().type == TokenType.SEMICOLON:
                return
            
        match self.peek().type:
            case 'CLASS':
                return
            case 'FUN':
                return
            case 'VAR':
                return
            case 'FOR':
                return
            case 'IF':
                return
            case 'WHILE':
                return
            case 'PRINT':
                return
            case 'RETURN':
                return
        
        self.advance()

def test_parser():
    from scanner import Scanner
    from error_handler import ErrorHandler

    def parse(source):
        scanner = Scanner(source, ErrorHandler())
        parser = Parser(scanner.scan_tokens(), ErrorHandler())
        return parser.parse()

    # Test precedence and assossiativty
    assert parse("2;") == Literal(2)
    assert parse('"hello";') == Literal('hello')
    assert parse("true;") == Literal(True)
    assert parse("false;") == Literal(False)
    assert parse("nil;") == Literal(None)
    print(parse("-2+3;"))
    #assert parse("-2+3;") == Binary(Unary(Token(TokenType.MINUS, '-', None, 1), Literal(2)), Token(TokenType.PLUS, '+', None, 1), Literal(3))
    #assert parse("2+3*4;") == Binary(Literal(2), Token(TokenType.PLUS, '+', None, 1), Binary(Literal(3), Token(TokenType.STAR, '*', None, 1), Literal(4)))


    print('Good Tests!')

#test_parser()

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
            statements.append(self.declaration())

        return statements

    def expression(self):
        return self.assignment()

    def declaration(self):
        try:
            if self.match(TokenType.VAR):
                return self.var_declaration()
            else: 
                return self.statement()
        except ParseError as error: 
            self.synchronize()
            return None
        
    def statement(self):
        if self.match(TokenType.FOR):
            return self.for_statement()
        if self.match(TokenType.IF):
            return self.if_statement()
        if self.match(TokenType.PRINT):
            return self.print_statement()
        if self.match(TokenType.WHILE):
            return self.while_statement()
        if self.match(TokenType.LEFT_BRACE):
            return Block(self.block())
        return self.expression_statement()
    
    def for_statement(self):
        self.consume(TokenType.LEFT_PAREN,  "Expect '(' after 'for'.")

        if self.match(TokenType.SEMICOLON):
            initializer = None
        elif self.match(TokenType.VAR):
            initializer = self.var_declaration()
        else: 
            initializer = self.expression_statement()

        condition = None
        if not self.check(TokenType.SEMICOLON):
            condition = self.expression()
        self.consume(TokenType.SEMICOLON,  "Expect ';' after loop condition.")

        increment = None
        if not self.check(TokenType.RIGHT_PAREN):
            increment = self.expression()
        self.consume(TokenType.RIGHT_PAREN,  "Expect ')' after for clauses.")

        body = self.statement()

        if increment is not None:
            body = Block([body, ExprStmt(increment)])
        
        if condition is None:
            condition = Literal(True)
        body = WhileStmt(condition, body)

        if initializer is not None: 
            body = Block([initializer, body])

        return body
    
    def if_statement(self):
        self.consume(TokenType.LEFT_PAREN,  "Expect '(' after 'if'.")
        test = self.expression()
        self.consume(TokenType.RIGHT_PAREN, "Expect ')' after if condition.")

        consequence = self.statement()
        alternative = None
        if self.match(TokenType.ELSE):
            alternative = self.statement()
        return IfStmt(test, consequence, alternative)
    
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
    
    def while_statement(self):
        self.consume(TokenType.LEFT_PAREN,  "Expect '(' after 'while'.")
        test = self.expression()
        self.consume(TokenType.RIGHT_PAREN, "Expect ')' after condition.")
        body = self.statement()
        return WhileStmt(test, body)
    
    def expression_statement(self):
        value = self.expression()
        self.consume(TokenType.SEMICOLON, "Expect ';' after expression.")
        return ExprStmt(value)
    
    def block(self):
        statements = []

        while not self.check(TokenType.RIGHT_BRACE) and not self.is_at_end():
            statements.append(self.declaration())

        self.consume(TokenType.RIGHT_BRACE, "Expect '}' after block.")
        return statements
    
    def assignment(self):
        expr = self._or()

        if self.match(TokenType.EQUAL):
            equals = self.previous()
            value = self.assignment()

            if isinstance(expr, Variable):
                name = expr.name
                return Assign(name, value)
            
            self.error(equals, "Invalid assignment target.")

        return expr
    
    def _or(self):
        expr = self._and()
    
        while self.match(TokenType.OR):
            operator = self.previous()
            right = self._and()
            expr = Logical(expr, operator, right)
        
        return expr
    
    def _and(self):
        expr = self.equality()

        while self.match(TokenType.AND):
            operator = self.previous()
            right = self.equality()
            expr = Logical(expr, operator, right)

        return expr

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
        elif self.match(TokenType.IDENTIFIER):
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
        if self.check(type):
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
    assert parse('2;') == [ExprStmt(Literal(2))]
    assert parse('true;') == [ExprStmt(Literal(True))]
    assert parse('false;') == [ExprStmt(Literal(False))]
    assert parse('nil;') == [ExprStmt(Literal(None))]
    assert parse('print "hello";') == [Print(Literal('hello'))]
    assert parse('print 2;') == [Print(Literal(2))] 
    test = parse('var a = 0;\n'
              'var temp;\n'
              'for (var b = 1; a < 10000; b = temp + b) {\n'
              'print a;\n'
              'temp = a;\n'
              'a = b;\n'
              '}')
    print(test)
    print('All tests passed!')

if __name__ == '__main__':
    test_parser()


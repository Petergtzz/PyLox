# scanner.py

from tokens import Token
from token_type import TokenType

class Scanner:
    '''
    This class reads raw source code and creates tokens from meaningful
    characters. The tokens will then be fed to the parser as a list. 

    Attributes
    ----------
    source : str
        raw source code
    error_handler : class
        reports errors
    tokens : list
        stores individual tokens from raw source code
    start : int
        points to the first character in the lexeme being scanned
    current : int
        points at the character currently being considered
    line : int 
        tracks what source line current is on
        
    '''
    def __init__(self, source, error_handler):
        self.source = source 
        self.error_handler = error_handler
        self.tokens = []
        self.start = 0
        self.current = 0
        self.line = 1

        self.keywords = {
            'and': TokenType.AND,
            'class': TokenType.CLASS,
            'else':  TokenType.ELSE,
            'false': TokenType.FALSE,
            'for':   TokenType.FOR,
            'fun':   TokenType.FUN,
            'if':    TokenType.IF,
            'nil':   TokenType.NIL,
            'or':    TokenType.OR,
            'print': TokenType.PRINT,
            'return': TokenType.RETURN,
            'super': TokenType.SUPER,
            'this':  TokenType.THIS,
            'true':  TokenType.TRUE,
            'var':   TokenType.VAR,
            'while': TokenType.WHILE,
        }

    def scan_tokens(self):
        while not self.is_at_end():
            self.start = self.current
            self.scan_token()
        self.tokens.append(Token(TokenType.EOF, '', None, self.line))
        return self.tokens
    
    def scan_token(self):
        char = self.advance()
        match char:
            case '(':
                self.add_token(TokenType.LEFT_PAREN)
            case ')':
                self.add_token(TokenType.RIGHT_PAREN)
            case '{':
                self.add_token(TokenType.LEFT_BRACE)
            case '}':
                self.add_token(TokenType.RIGHT_BRACE)
            case ',':
                self.add_token(TokenType.COMMA)
            case '.':
                self.add_token(TokenType.DOT)
            case '-':
                self.add_token(TokenType.MINUS)
            case '+':
                self.add_token(TokenType.PLUS)
            case ';':
                self.add_token(TokenType.SEMICOLON)
            case '*':
                self.add_token(TokenType.STAR)
            # Two-char-tokens
            case '!':
                self.add_token(TokenType.BANG_EQUAL if self.match('=') else TokenType.BANG)
            case '=':
                self.add_token(TokenType.EQUAL_EQUAL if self.match('=') else TokenType.EQUAL)
            case '<':
                self.add_token(TokenType.LESS_EQUAL if self.match('=') else TokenType.LESS)
            case '>':
                self.add_token(TokenType.GREATER_EQUAL if self.match('=') else TokenType.GREATER)
            case '/':
                if self.match('/'):
                    while self.peek() != '\n' and not self.is_at_end():
                        self.advance()
                else: 
                    self.add_token(TokenType.SLASH)
            case ' ':
                return None
            case '\r':
                return None
            case '\t':
                return None
            case '\n':
                self.line += 1
            case '"':
                self.string()
            case _:
                if self.is_digit(char):
                    self.number()
                elif self.is_alpha(char):
                    self.identifier()
                else:
                    self.error_handler.error(self.line, 'Unexpected character.')
 
    def identifier(self):
        while self.is_alpha_numeric(self.peek()):
            self.advance()

        text = self.source[self.start:self.current]
        type = self.keywords.get(text)
        if type is None:
            type = TokenType.IDENTIFIER
        self.add_token(type)
                    
    def number(self):
        while self.is_digit(self.peek()):
            self.advance()

        # Look for fractional part
        if self.peek() == '.' and self.is_digit(self.peek_next()):
            self.advance()

            while self.is_digit(self.peek()):
                self.advance()

        self.add_token(TokenType.NUMBER, float(self.source[self.start:self.current]))
                
    def string(self):
        while self.peek() != '"' and not self.is_at_end():
            if self.peek() == '\n':
                self.line += 1
            self.advance()
        
        if self.is_at_end():
            self.error_handler.error(self.line, 'Unterminated string.')
            return None

        # Closing ".
        self.advance()

        # Trim the surrounding quotes
        value = self.source[self.start + 1: self.current - 1]
        self.add_token(TokenType.STRING, value)

    def match(self, expected):
        if self.is_at_end():
            return False
        if self.source[self.current] != expected:
            return False
        
        self.current += 1
        return True
    
    # Looksahead, but does not consume the character
    def peek(self):
        return self.source[self.current] if not self.is_at_end() else '\0'
    
    def peek_next(self):
        if self.current + 1 >= len(self.source):
            return '\0'
        else:
            return self.source[self.current + 1] 
        
    def is_alpha(self, char):
        return ('a' <= char <= 'z' or 'A' <= char <= 'Z') or char == '_'
    
    def is_alpha_numeric(self, char):
        return self.is_alpha(char) or self.is_digit(char)
    
    def is_digit(self, char):
        return char >= '0' and char <= '9'
    
    # Tells us if we have consumed all the characters
    def is_at_end(self):
        return self.current >= len(self.source)
    
    # Consumes the next character in the source file and returns it
    def advance(self):
        current_char = self.source[self.current]
        self.current += 1
        return current_char

    def add_token(self, type, literal=None):
        text = self.source[self.start:self.current]
        self.tokens.append(Token(type, text, literal, self.line))

def test_scanner():
    from error_handler import ErrorHandler

    def scan(source):
        scanner = Scanner(source, ErrorHandler())
        tokens = scanner.scan_tokens()
        return [getattr(token.type, 'name') for token in tokens]
    
    toktypes = scan("""( ) { } , . - + * = ==
                        // This is a comment
                        / ; ! != < <= > >=""") 
    assert toktypes == ['LEFT_PAREN', 'RIGHT_PAREN', 'LEFT_BRACE', 'RIGHT_BRACE',
                        'COMMA', 'DOT', 'MINUS', 'PLUS', 'STAR', 'EQUAL', 'EQUAL_EQUAL', 'SLASH',
                        'SEMICOLON', 'BANG', 'BANG_EQUAL', 'LESS', 'LESS_EQUAL',
                        'GREATER', 'GREATER_EQUAL', 'EOF']
    
    toktypes = scan("and class else false for fun if nil or print return super this true var while")
    assert toktypes == ['AND', 'CLASS', 'ELSE', 'FALSE', 'FOR', 'FUN', 'IF', 'NIL',
                         'OR', 'PRINT', 'RETURN', 'SUPER', 'THIS', 'TRUE',
                         'VAR', 'WHILE', 'EOF']
    
    toktypes = scan('123 123.0 "hello" "hello\nworld"')
    assert toktypes == ['NUMBER', 'NUMBER', 'STRING', 'STRING', 'EOF']

    toktypes = scan('abc abc123 _abc_123')
    assert toktypes == ['IDENTIFIER', 'IDENTIFIER', 'IDENTIFIER', 'EOF']
    
    print('Good Tests!')

#test_scanner()

    

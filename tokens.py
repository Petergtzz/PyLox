# tokens.py

class Token:
    '''
    This class stores information about individual tokens. A token is a category assigned
    to text words, also known as lexemes.  
    '''
    __slots__ = ['type', 'lexeme', 'literal', 'line']
    def __init__(self, type, lexeme, literal, line):
        self.type = type
        self.lexeme = lexeme
        self.literal = literal
        self.line = line

    def __str__(self):
        #return getattr(self.type, 'name')
        return self.lexeme
    
    def __repr__(self):
        return f'Token(type={self.type}, lexeme={self.lexeme!r}, value={self.literal!r}, line={self.line!r})'
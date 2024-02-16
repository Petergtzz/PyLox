# tokens.py

class Token:
    '''
    This class represents an individual token. 

    Attributes
    ----------
    type : tokentype object
        category assigned to a word
    lexeme : str
        sequence of characters forming an actual word
    literal : str or float
        actual values for strings and numbers
    line : int
        track where the token was found

    '''
    __slots__ = ['type', 'lexeme', 'literal', 'line']
    def __init__(self, type, lexeme, literal, line):
        self.type = type
        self.lexeme = lexeme
        self.literal = literal
        self.line = line

    def __str__(self):
        return self.lexeme
    
    def __repr__(self):
        return f'Token(type={self.type}, lexeme={self.lexeme!r}, value={self.literal!r}, line={self.line!r})'
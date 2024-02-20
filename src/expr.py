# expr.py

from tokens import Token
from token_type import TokenType

class Node:
    '''
    This is a base class to construct non-terminal nodes. Each instance 
    represents a single AST node.
    '''
     # Track define AST node-names for some later sanity checks
    _nodenames = set()
    @classmethod
    def __init_subclass__(cls):
        Node._nodenames.add(cls.__name__)

    _fields = []
    def __init__(self, *args):
        assert len(args) == len(type(self)._fields)
        # Match the instance field names to it's corresponging arguments
        for name, val in zip(type(self)._fields, args):
            setattr(self, name, val)

    def __repr__(self):
        args = ', '.join(f'{key}={value!r}' for key, value in vars(self).items())
        return f'{type(self).__name__}({args})'

    def __eq__(self, other):
        return type(self) == type(other) and vars(self) == vars(other)

# -- Expressions represent values
class Expr(Node):
    pass

class Binary(Expr):
    _fields = ['left', 'op', 'right']

class Grouping(Expr):
    _fields = ['value']

class Literal(Expr):
    _fields = ['value']

class Unary(Expr):
    _fields = ['op', 'right']

class Variable(Expr):
    _fields = ['name']

class Assign(Expr):
    _fields = ['name', 'value']

# -- Statements represent actions with no associated value
class Statement(Node):
    pass

class Print(Statement):
    _fields = ['value']

class ExprStmt(Statement):
    _fields = ['value']

class Block(Statement):
    _fields = ['statements']

# -- Declarations are special kinds of statements that declare the existence of something
class Declaration(Statement):
    pass

class VarDeclaration(Declaration):
    _fields = ['name', 'initializer']

class NodeVisitor:
    '''
    This class implements the vistor pattern. Subclasses can provide
    custom visit methods for different types of AST nodes.
    '''
    def __init_subclass__(cls):
        # Ensure that each visit method in the subclass corresponds 
        # to a valid AST node type.
        visitors = { key for key in cls.__dict__ if key.startswith('visit_') }
        assert all(key[6:] in Node._nodenames for key in visitors)

    def visit(self, node):
        method = f'visit_{type(node).__name__}'
        return getattr(self, method)(node)
    
class ASTPrinter(NodeVisitor):
    def print_ast(self, node):
        return f'{self.visit(node)}'
    
    def visit_Literal(self, node):
        if node.value is None:
            return "nil"
        elif node.value is True:
            return "true"
        elif node.value is False:
            return "false"
        else:
            return repr(node.value)
    
    def visit_Binary(self, node):
        return f'({node.op} {self.visit(node.left)} {self.visit(node.right)})'
    
    def visit_Unary(self, node):
        return f'({node.op} {self.visit(node.right)})'

    def visit_Grouping(self, node):
        return f'(group {self.visit(node.value)})'
    
if __name__ == '__main__':
    printer = ASTPrinter()

    # Evaluate: -123 * (45.67)
    test_1 = Binary(
    Unary(
        Token(TokenType.MINUS, '-', None, 1),
        Literal(123)),
    Token(TokenType.STAR, '*', None, 1),
    Grouping(
        Literal(45.67)),
    )

    # Evaluate: 1 + 8 * 9 + 14 == 38
    test_2 = Binary(
        Binary(
            Binary(
                Literal(1),
                Token(TokenType.PLUS, '+', None, 1),
                Grouping(
                    Binary(
                        Literal(8),
                        Token(TokenType.STAR, '*', None, 1),
                        Literal(9)))
                ),
            Token(TokenType.PLUS, '+', None, 1),
            Literal(14)
        ),
    Token(TokenType.EQUAL_EQUAL, '==', None, 1),
    Literal(38)
    )

    result_1 = printer.print_ast(test_1)  
    result_2 = printer.print_ast(test_2)
    assert result_1 == '(* (- 123) (group 45.67))' # Use the name of the token, not the value
    assert result_2 == '(== (+ (+ 1 (group (* 8 9))) 14) 38)'
    print('Good Tests!')

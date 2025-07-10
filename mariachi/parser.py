"""The parser module for the Mariachi Lang toy language."""

from .lexer import *
from .nodes import *
from .token import *

class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.tok_idx = 1
        self.advance_tok()

    def advance_tok(self):
        self.tok_idx += 1
        if self.tok_idx < len(self.tokens):
            self.current_tok = self.tokens[self.tok_idx]
        return self.current_tok
    
    def factor(self):
        """Logic for handling factors."""
        tok = self.current_tok
        # Checks if our current token is a number type
        if tok in (TT_INT, TT_FLOAT):
            self.advance_tok
            return NumberNode(tok)
        
    def term(self):
        """Creates our terms."""
        return self.binary_operation(self.factor, (TT_DIV, TT_MUL))

    def expr(self):
        """Creates our expression."""
        return self.binary_operation(self.factor, (TT_PLUS, TT_MINUS))

    def binary_operation(self, func, ops):
        """Refactored logic for handling operators"""
        left = func()

        while self.current_tok in ops:
            # We assign the operation tokens and right factor
            op_tok = self.current_tok
            right = func()
            # We have to advance to prevent infinite loops
            self.advance_tok()
            # Reassign to a BindaryOpNode
            left = BindingOperatorNode(left, op_tok, right)
        return left

def run(fn, code):
    """The code runner used to parse the code and tokenize inputs."""
    lexer = Lexer(fn, code)
    tokens, error = lexer.make_tokens()
    return tokens, error
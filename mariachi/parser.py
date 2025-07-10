"""The parser module for the Mariachi Lang toy language."""

from .lexer import *
from .nodes import *
from .token import *

class Parser:
    """The parser class for our language."""
    def __init__(self, tokens):
        self.tokens = tokens
        self.tok_idx = -1
        self.advance()

    def advance(self):
        """Advance through our tokens."""
        self.tok_idx += 1
        if self.tok_idx < len(self.tokens):
            self.current_tok = self.tokens[self.tok_idx]
        return self.current_tok

    
    def parse(self):
        """Parser function for the grammar rules."""
        res = self.expr()
        if not res.error and self.current_tok.type != TT_EOF:
            return res.failure(
                SintaxisInvalidoError(self.current_tok.pos_start, self.current_tok.pos_end, "Expected '+', '/', '+', 'or' -")
                )
        return res
    
    def factor(self):
        """Logic for handling factors."""
        res = ParseResult()
        tok = self.current_tok
        # Checks to see if our token type is a plus or a minus
        if tok.type in (TT_PLUS, TT_MINUS):
            res.register(self.advance())
            factor = res.register(self.factor())
            # Check for any errors
            if res.error:
                return res
            return res.success(UnaryOpNode(tok, factor))
        # Checks if our current token is a number type
        elif tok.type in (TT_INT, TT_FLOAT):
            res.register(self.advance())
            return res.success(NumberNode(tok))
        elif tok.type == TT_LPAREN:
            res.register(self.advance())
            expr = res.register(self.expr())
            # Check for errors
            if res.error:
                return res
            if self.current_tok.type == TT_RPAREN:
                res.register(self.advance())
                return res.success(expr)
            else:
                return res.failure(
                    SintaxisInvalidoError(self.current_tok.pos_start, self.current_tok.pos_end, "Expected ')'")
                    )

        return res.failure(
            SintaxisInvalidoError(tok.pos_start, tok.pos_end, 'Expected int or float')
            )
        
    def term(self):
        """Creates our terms."""
        return self.binary_operation(self.factor, (TT_DIV, TT_MUL))

    def expr(self):
        """Creates our expression."""
        return self.binary_operation(self.term, (TT_PLUS, TT_MINUS))

    def binary_operation(self, func, ops):
        """Refactored logic for handling operators."""
        res = ParseResult()
        left = res.register(func())
        # Early exit if an error is found
        if res.error:
            return res

        while self.current_tok.type in ops:
            # We assign the operation tokens
            op_tok = self.current_tok
            # We have to advance to prevent infinite loops
            res.register(self.advance())
            # We assign the right factor
            right = res.register(func())
            # Early exit if an error is found
            if res.error:
                return res
            # Reassign to a BindaryOpNode
            left = BinaryOpNode(left, op_tok, right)
        return res.success(left)
    
class ParseResult:
    """A class for handling the results from parsing."""
    def __init__(self):
        self.error = None
        self.node = None

    def register(self, res):
        """Checks for errors."""
        if isinstance(res, ParseResult):
            if res.error:
                self.error = res.error
            return res.node
        return res

    def success(self, node):
        self.node = node
        return self

    def failure(self, error):
        self.error = error
        return self

def run(fn, code):
    """The code runner used to parse the code and tokenize inputs."""
    # Generates the tokens
    lexer = Lexer(fn, code)
    tokens, error = lexer.make_tokens()
    if error:
        return None, error

    # Generates the AST
    parser = Parser(tokens)
    ast = parser.parse()
    return ast.node, ast.error
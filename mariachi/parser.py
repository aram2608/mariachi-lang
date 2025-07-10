"""The parser module for the Mariachi Lang toy language."""

from .lexer import *
from .nodes import *
from .token import *
from .interpreter import *
from .context import *

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
    
    def atom(self):
        """Logic for handling atoms."""
        res = ParseResult()
        tok = self.current_tok
        # Checks if our current token is a number type
        if tok.type in (TT_INT, TT_FLOAT):
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
            SintaxisInvalidoError(tok.pos_start, tok.pos_end, "Expected int, float, '+', '-', or '(')")
            )
    
    def power(self):
        """Handles powers."""
        return self.binary_operation(self.atom,(TT_POW, ), self.factor)

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
        return self.power()

    def term(self):
        """Creates our terms."""
        return self.binary_operation(self.factor, (TT_DIV, TT_MUL))

    def expr(self):
        """Creates our expression."""
        return self.binary_operation(self.term, (TT_PLUS, TT_MINUS))

    def binary_operation(self, func_a, ops, func_b=None):
        """Refactored logic for handling operators."""
        if func_b == None:
            func_b = func_a

        res = ParseResult()
        left = res.register(func_a())
        # Early exit if an error is found
        if res.error:
            return res

        while self.current_tok.type in ops:
            # We assign the operation tokens
            op_tok = self.current_tok
            # We have to advance to prevent infinite loops
            res.register(self.advance())
            # We assign the right factor
            right = res.register(func_b())
            # Early exit if an error is found
            if res.error:
                return res
            # Reassign to a BindaryOpNode
            left = BinaryOpNode(left, op_tok, right)
        return res.success(left)

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
    if ast.error:
        return None, ast.error
    
    # Run interpreter
    interpreter = Interpreter()
    context = Context('<programma>')
    result = interpreter.visit(ast.node, context)
    return result.value, result.error
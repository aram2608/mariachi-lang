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
                SintaxisInvalidoError(self.current_tok.pos_start, self.current_tok.pos_end, "'+', '/', '+', o '-' esperado")
                )
        return res
    
    def atom(self):
        """Logic for handling atoms."""
        res = ParseResult()
        tok = self.current_tok

        # Checks if our current token is a number type
        if tok.type in (TT_INT, TT_FLOAT):
            res.register_advancement()
            self.advance()
            return res.success(NumberNode(tok))
        
        # Check for identifier
        elif tok.type == TT_IDENTIFIER:
            res.register_advancement()
            self.advance()
            return res.success(VarAccessNode(tok))
        
        # Boolean check
        elif tok.matches(TT_KEYWORD, 'cierto'):
            res.register_advancement()
            self.advance()
            return res.success(NumberNode(Token(TT_INT, 1, tok.pos_start, tok.pos_end)))

        elif tok.matches(TT_KEYWORD, 'falso'):
            res.register_advancement()
            self.advance()
            return res.success(NumberNode(Token(TT_INT, 0, tok.pos_start, tok.pos_end)))

        # Parenthesis check
        elif tok.type == TT_LPAREN:
            res.register_advancement()
            self.advance()
            expr = res.register(self.expr())
            # Check for errors
            if res.error:
                return res
            if self.current_tok.type == TT_RPAREN:
                res.register_advancement()
                self.advance()
                return res.success(expr)
            else:
                return res.failure(
                    SintaxisInvalidoError(self.current_tok.pos_start, self.current_tok.pos_end, "')' esperado")
                    )
        # If statement
        elif tok.matches(TT_KEYWORD, 'si'):
            if_expr = res.register(self.if_expr())
            if res.error: return res
            return res.success(if_expr)

        return res.failure(
            SintaxisInvalidoError(tok.pos_start, tok.pos_end, "int, float, identificador, '+', '-', o '(') esperado")
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
            res.register_advancement()
            self.advance()
            factor = res.register(self.factor())
            # Check for any errors
            if res.error:
                return res
            return res.success(UnaryOpNode(tok, factor))
        return self.power()
    
    def statements(self):
        res = ParseResult()
        statements = []

        if self.current_tok.type != TT_LBRACE:
            return res.failure(SintaxisInvalidoError(
                self.current_tok.pos_start, self.current_tok.pos_end, "'{' esperado"
            ))

        res.register_advancement()
        self.advance()

        while self.current_tok.type != TT_RBRACE:
            stmt = res.register(self.expr())
            if res.error: return res
            statements.append(stmt)

            # Optional: allow semicolon or newlines to separate
            if self.current_tok.type == TT_EOF:
                return res.failure(SintaxisInvalidoError(
                    self.current_tok.pos_start, self.current_tok.pos_end, "'}' esperado"
                ))

        res.register_advancement()
        self.advance()

        return res.success(BlockNode(statements))


    def term(self):
        """Creates our terms."""
        return self.binary_operation(self.factor, (TT_DIV, TT_MUL, TT_MOD, TT_FLOORDIV))
    
    def arith_expr(self):
        """Handles arithmetic logic."""
        return self.binary_operation(self.term, (TT_PLUS, TT_MINUS))
    
    def comp_expr(self):
        """Handles comparison expression."""
        res = ParseResult()
        
        if self.current_tok.matches(TT_KEYWORD, 'jamas'):
            op_tok = self.current_tok
            res.register_advancement()
            self.advance()

            node = res.register(self.comp_expr())
            if res.error: return res
            return res.success(UnaryOpNode(op_tok, node))
        
        node = res.register(self.binary_operation(self.arith_expr, (TT_EE, TT_NE, TT_LT, TT_LTE, TT_GT, TT_GTE)))
        if res.error:
            return res.failure(SintaxisInvalidoError(
                self.current_tok.pos_start, self.current_tok.pos_end, "int, float, identificador, '+', '-', '(', o 'jamas' esperado"
                ))
        return res.success(node)
    
    def if_expr(self):
        res = ParseResult()
        cases = []
        else_case = None

        if not self.current_tok.matches(TT_KEYWORD, 'si'):
            return res.failure(SintaxisInvalidoError(
                self.current_tok.pos_start, self.current_tok.pos_end, f"'si' esperado"))

        res.register_advancement()
        self.advance()

        condition = res.register(self.comp_expr())
        if res.error: return res

        if self.current_tok.matches(TT_KEYWORD, 'pues'):
            res.register_advancement()
            self.advance()
            expr = res.register(self.expr())
            if res.error: return res
            cases.append((condition, expr))
        elif self.current_tok.type == TT_LBRACE:
            expr = res.register(self.statements())
            if res.error: return res
            cases.append((condition, expr))
        else:
            return res.failure(SintaxisInvalidoError(
                self.current_tok.pos_start, self.current_tok.pos_end,
                "'pues' o '{' esperado"))

        while self.current_tok.matches(TT_KEYWORD, 'quizas'):
            res.register_advancement()
            self.advance()

            condition = res.register(self.comp_expr())
            if res.error: return res

            if self.current_tok.matches(TT_KEYWORD, 'pues'):
                res.register_advancement()
                self.advance()
                expr = res.register(self.expr())
                if res.error: return res
                cases.append((condition, expr))
            elif self.current_tok.type == TT_LBRACE:
                expr = res.register(self.statements())
                if res.error: return res
                cases.append((condition, expr))
            else:
                return res.failure(SintaxisInvalidoError(
                    self.current_tok.pos_start, self.current_tok.pos_end,
                    "'pues' o '{' esperado"))

        if self.current_tok.matches(TT_KEYWORD, 'sino'):
            res.register_advancement()
            self.advance()

            if self.current_tok.type == TT_LBRACE:
                else_case = res.register(self.statements())
            else:
                else_case = res.register(self.expr())
            if res.error: return res

        return res.success(IfNode(cases, else_case))

    def expr(self):
        """Creates our expression."""
        res = ParseResult()

        # Print statement
        if self.current_tok.matches(TT_KEYWORD, 'canta'):
            res.register_advancement()
            self.advance()

            expr = res.register(self.expr())
            if res.error:
                return res
            return res.success(PrintNode(expr))

        # Check to make sure the token matches a keyword
        if self.current_tok.matches(TT_KEYWORD, 'sea'):
            res.register_advancement()
            self.advance()
            
            # Check to make sure following token is an indentifier
            if self.current_tok.type != TT_IDENTIFIER:
                return res.failure(SintaxisInvalidoError(
                    self.current_tok.pos_start, self.current_tok.pos_end, 'Identificador esperado'))
            
            # Assigns the variable name
            var_name = self.current_tok
            res.register_advancement()
            self.advance()

            # Check to ensure that following a var name is an =
            if self.current_tok.type != TT_EQ:
                return res.failure(SintaxisInvalidoError(
                    self.current_tok.pos_start, self.current_tok.pos_end, "'=' esperado"))
            
            # Assign a new expression to the created variable
            res.register_advancement()
            self.advance()
            expr = res.register(self.expr())
            if res.error: return res
            return res.success(VarAssignNode(var_name, expr))

        node = res.register(self.binary_operation(self.comp_expr, ((TT_KEYWORD, "y"), (TT_KEYWORD, 'o'))))

        if res.error: 
            return res.failure(
                SintaxisInvalidoError(self.current_tok.pos_start, self.current_tok.pos_end, 
                                    "'sea', int, float, identificador, '+', '-', '(', o 'jamas' esperado"))
        return res.success(node)

    def binary_operation(self, func_a, ops, func_b=None):
        """Refactored logic for handling operators."""
        if func_b == None:
            func_b = func_a

        res = ParseResult()
        left = res.register(func_a())
        # Early exit if an error is found
        if res.error:
            return res

        while self.current_tok.type in ops or (self.current_tok.type, self.current_tok.value) in ops:
            # We assign the operation tokens
            op_tok = self.current_tok

            # We have to advance to prevent infinite loops

            res.register_advancement()
            self.advance()

            # We assign the right factor
            right = res.register(func_b())

            # Early exit if an error is found
            if res.error:
                return res

            # Reassign to a BindaryOpNode
            left = BinaryOpNode(left, op_tok, right)
        return res.success(left)

global_symbol_table = SymbolTable()
global_symbol_table.set("nada", Number(0))

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
    context.symbol_table = global_symbol_table
    result = interpreter.visit(ast.node, context)
    return result.value, result.error
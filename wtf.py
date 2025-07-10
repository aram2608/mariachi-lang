
class Context:
    """The context for the runtime of a Mariachi Lang program."""
    def __init__(self, display_name, parent=None, parent_entry_pos=None):
        self.display_name = display_name
        self.parent = parent
        self.parent_entry_pos = parent_entry_pos
        self.symbol_table = Noneclass Error:
    """The custom error classes of the Mariachi Lang."""
    def __init__(self, pos_start, pos_end, error_name, details):
        self.pos_start = pos_start
        self.pos_end = pos_end
        self.error_name = error_name
        self.details = details

    def as_string(self):
        """Converts our error type into a string with provided details."""
        result = f'{self.error_name}: {self.details}'
        result += f'\nFile {self.pos_start.fn}, line {self.pos_end.ln} + 1'
        result += '\n' + string_with_arrows(self.pos_start.ftxt, self.pos_start, self.pos_end)
        return result
    
class InesperadoError(Error):
    def __init__(self, pos_start, pos_end, details):
        """Subclass for unexpected character inputs."""
        super().__init__(pos_start, pos_end, 'Caracter Inesperado', details)

class SintaxisInvalidoError(Error):
    def __init__(self, pos_start, pos_end, details=''):
        super().__init__(pos_start, pos_end, 'Sintaxis Invalido', details)

class EjecucionError(Error):
    def __init__(self, pos_start, pos_end, details, context):
        super().__init__(pos_start, pos_end, 'Ejecucion error', details)
        self.context = context

    def as_string(self):
        """Custom method to represent errors as strings."""
        result = self.genereate_traceback()
        result += f'{self.error_name}: {self.details}'
        result += '\n' + string_with_arrows(self.pos_start.ftxt, self.pos_start, self.pos_end)
        return result

    def genereate_traceback(self):
        """Generates a traceback for error handling."""
        result = ''
        pos = self.pos_start
        ctx = self.context

        while ctx:
            result = f' Fichero {pos.fn}, lina {str(pos.ln + 1)}, en {ctx.display_name}\n'
            pos = ctx.parent_entry_pos
            ctx = ctx.parent
        return 'Retrazo (funcion mas reciente):\n' + result

def string_with_arrows(code, pos_start, pos_end):
    """Adds arrows to point to where the error occured."""
    YELLOW = "\033[93m"
    BOLD = '\033[1m'
    RESET = '\033[0m'
    # Holds our final result
    result = ''

    # Calculates indices
    idx_start = max(code.rfind('\n', 0, pos_start.idx), 0)
    idx_end = code.find('\n', idx_start + 1)
    if idx_end < 0:
        idx_end = len(code)

    # Generate each line
    line_count = pos_end.ln - pos_start.ln + 1
    for i in range(line_count):
        line = code[idx_start:idx_end]
        col_start = pos_start.col if i == 0 else 0
        col_end = pos_end.col if i == line_count - 1 else len(line) - 1

        # Append to result
        num_arrows = max(1, col_end - col_start)
        result += f"{BOLD}{line}{RESET}\n"
        result += ' ' * col_start + f"{YELLOW}{'^' * num_arrows}{RESET}"

        # Recalculate indices
        idx_start = idx_end
        idx_end = code.find('\n', idx_start + 1)
        if idx_end < 0: idx_end = len(code)
    return result.replace('\t', '')
from .numbers import *
from .token import *
from .results import *
from .context import *
from .errors import *

class Interpreter:
    """The interpreter for the Mariachi Lang toy language."""
    def visit(self, node, context):
        # Creates method name from the node classes
        method_name = f'visit_{type(node).__name__}'
        # The get attribute method returns a named attribute from an object
        method = getattr(self, method_name, self.no_visit_method)
        return method(node, context)
    
    def no_visit_method(self, node, context):
        raise Exception(f'No visit_{type(node).__name__} method defined.')
    
    def visit_NumberNode(self, node, context):
        return RTResult().success(Number(node.tok.value).set_context(context).set_position(node.pos_start, node.pos_end))

    def visit_BinaryOpNode(self, node, context):
        res = RTResult()
        left = res.register(self.visit(node.left_node, context))
        if res.error:
            return res
        right = res.register(self.visit(node.right_node, context))
        if res.error:
            return res

        if node.op_tok.type == TT_PLUS:
            result, error = left.added_to(right)
        elif node.op_tok.type == TT_MINUS:
            result, error = left.subbed_by(right)
        elif node.op_tok.type == TT_MUL:
            result, error = left.multed_by(right)
        elif node.op_tok.type == TT_DIV:
            result, error = left.divided_by(right)
        elif node.op_tok.type == TT_POW:
            result, error = left.power_by(right)

        if error:
            return res.failure(error)
        return res.success(result.set_position(node.pos_start, node.pos_end))

    def visit_UnaryOpNode(self, node, context):
        res = RTResult()
        number = res.register(self.visit(node.node, context))
        if res.error:
            return res
        if node.op_tok.type == TT_MINUS:
            number, error = number.multed_by(Number(-1))

        if error:
            return res.failure(error)
        return res.success(number.set_position(node.pos_start, node.pos_end))
    
    def visit_VarAssignNode(self, node, context):
        res = RTResult()
        var_name = node.var_name_tok.value
        value = res.register(self.visit(node.value_node, context))
        if res.error: return res

        context.symbol_table.set(var_name, value)
        return res.success(value)

    def visit_VarAccessNode(self, node, context):
        res = RTResult()
        var_name = node.var_name_tok.value
        value = context.symbol_table.get(var_name)

        if not value:
            return res.failure(EjecucionError(
                node.pos_start, node.pos_end, f"'{var_name}' is not defined", context))
        return res.success(value)
    
class SymbolTable:
    def __init__(self):
        self.symbols = {}
        self.parent = None

    def get(self, name):
        """Function to get the value of a variable name."""
        value = self.symbols.get(name, None)
        if value == None and self.parent:
            return self.parent.get(name)
        return value
    
    def set(self, name, value):
        """Sets the key value pairs of the symbols dictionary."""
        self.symbols[name] = value

    def remove(self, name):
        """Removes a variable from the sybmols."""
        del self.symbols[name]
from .token import *
from .errors import *

class Lexer:
    def __init__(self, fn, text):
        # The input file name
        self.fn = fn
        # The processed text
        self.text = text
        # Tracks current position
        self.pos = Position(-1, 0, -1, fn, text)
        # Tracks current character, default is None type
        self.current_char = None
        self.advance()

    def advance(self):
        """A class method to increment position in text."""
        self.pos.advance(self.current_char)
        # Sets incremented character as the current character
        if self.pos.idx < len(self.text):
            self.current_char = self.text[self.pos.idx]
        else:
        # We need to set the current char back to None to prevent infinite loops
            self.current_char = None

    def make_tokens(self):
        """A class method to tokenize input text."""
        # Initialize an empty list to store the token
        tokens = []

        while self.current_char != None:
            if self.current_char in ' \t':
                self.advance()
            elif self.current_char in DIGITS:
                tokens.append(self.make_number())
            elif self.current_char in LETTERS:
                tokens.append(self.make_identifier())
            elif self.current_char == '+':
                tokens.append(Token(TT_PLUS, pos_start=self.pos))
                self.advance()
            elif self.current_char == '-':
                tokens.append(Token(TT_MINUS, pos_start=self.pos))
                self.advance()
            elif self.current_char == '*':
                tokens.append(Token(TT_MUL, pos_start=self.pos))
                self.advance()
            elif self.current_char == '/':
                tokens.append(Token(TT_DIV, pos_start=self.pos))
                self.advance()
            elif self.current_char == '^':
                tokens.append(Token(TT_POW, pos_start=self.pos))
                self.advance()
            elif self.current_char == '=':
                tokens.append(Token(TT_EQ, pos_start=self.pos))
                self.advance()
            elif self.current_char == '(':
                tokens.append(Token(TT_LPAREN, pos_start=self.pos))
                self.advance()
            elif self.current_char == ')':
                tokens.append(Token(TT_RPAREN, pos_start=self.pos))
                self.advance()
            else:
                pos_start = self.pos.copy()
                char = self.current_char
                self.advance()
                # Returns no tokens and bad character error
                return [], InesperadoError(pos_start, self.pos, char)
        tokens.append(Token(TT_EOF, pos_start=self.pos))
        return tokens, None
    
    def make_number(self):
        """A class to handle tokenization of numbers."""
        # We handle all numbers as strings for tokenization.
        num_str = ''
        dot_count = 0
        pos_start = self.pos.copy()

        # The logic for handling integers vs floating point values.
        while self.current_char != None and self.current_char in DIGITS + '.':
            if self.current_char == '.':
                if dot_count == 1: 
                    break
                dot_count += 1
                num_str += '.'
            else:
                num_str += self.current_char
            self.advance()
        # Tokenization logic following evaluation of token type.
        if dot_count == 0:
            return Token(TT_INT, int(num_str), pos_start, self.pos)
        else:
            return Token(TT_FLOAT, float(num_str, pos_start, self.pos))
        
    def make_identifier(self):
        """A function to tokenize keywords and identifiers."""
        id_string = ''
        pos_start = self.pos.copy()

        while self.current_char != None and self.current_char in LETTERS_DIGITS + "_":
            id_string += self.current_char
            self.advance()

        tok_type = TT_KEYWORD if id_string in KEYWORDS else TT_IDENTIFIER
        return Token(tok_type, id_string, pos_start, self.pos)
    
class Position:
    """A class to store the position of the different code attributes."""
    def __init__(self, idx, ln, col, fn, ftxt):
        """Initial parameters for the position class.
        Stores index, line, column, file name, and file text.
        """
        self.idx = idx
        self.ln = ln
        self.col = col
        self.fn = fn
        self.ftxt = ftxt

    def advance(self, current_char=None):
        """A function to advance through a file, line by line."""
        self.idx += 1
        self.col += 1
        # Checks for new lines
        if current_char == '\n':
            self.ln += 1
            self.col = 0

        return self
    
    def copy(self):
        """Copies all of the stored values at a given position."""
        return Position(self.idx, self.ln, self.col, self.fn, self.ftxt)class NumberNode:
    def __init__(self, tok):
        self.tok = tok
        self.pos_start = self.tok.pos_start
        self.pos_end = self.tok.pos_end
    
    def __repr__(self):
        """A custom representation method for our number node."""
        return f'{self.tok}'
    
class BinaryOpNode:
    def __init__(self, left_node, op_tok, right_node):
        self.left_node = left_node
        self.op_tok = op_tok
        self.right_node = right_node
        self.pos_start = self.left_node.pos_start
        self.pos_end = self.right_node.pos_end

    def __repr__(self):
        return f'({self.left_node}, {self.op_tok}, {self.right_node})'
    
class UnaryOpNode:
    def __init__(self, op_tok, node):
        self.op_tok = op_tok
        self.node = node
        self.pos_start = self.op_tok.pos_start
        self.pos_end = node.pos_end

    def __repr__(self):
        """Custom representation method."""
        return f'({self.op_tok}, {self.node})'
    
class VarAssignNode:
    def __init__(self, var_name_tok, value_node):
        self.var_name_tok = var_name_tok
        self.value_node = value_node

        self.pos_start = self.value_node.pos_start
        self.pos_end = self.value_node.pos_end

class VarAccessNode:
    def __init__(self, var_name_tok):
        self.var_name_tok = var_name_tok

        self.pos_start = self.var_name_tok.pos_start
        self.pos_end = self.var_name_tok.pos_endfrom .errors import *

class Number:
    """Class for defining arithmetic logic."""
    def __init__(self, value):
        self.value = value
        self.set_position()
        self.set_context()

    def set_position(self, pos_start=None, pos_end=None):
        """Sets positions for error tracking."""
        self.pos_start = pos_start
        self.pos_end = pos_end
        return self
    
    def added_to(self, other):
        if isinstance(other, Number):
            return Number(self.value + other.value).set_context(self.context), None
        
    def subbed_by(self, other):
        if isinstance(other, Number):
            return Number(self.value - other.value).set_context(self.context), None
        
    def multed_by(self, other):
        if isinstance(other, Number):
            return Number(self.value * other.value).set_context(self.context), None
        
    def divided_by(self, other):
        if isinstance(other, Number):
            if other.value == 0:
                return None, EjecucionError(
                    other.pos_start, other.pos_end, 'Division por zero',
                    self.context
                )
            return Number(self.value / other.value).set_context(self.context), None
        
    def power_by(self, other):
        if isinstance(other, Number):
            return Number(self.value ** other.value).set_context(self.set_context), None
        
    def set_context(self, context=None):
        self.context = context
        return self
        
    def __repr__(self):
        return str(self.value)from .lexer import *
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
        
        # Check for identifier
        elif tok.type == TT_IDENTIFIER:
            res.register(self.advance())
            return res.success(VarAccessNode(tok))

        # Parenthesis check
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
        res = ParseResult()

        # Check to make sure the token matches a keyword
        if self.current_tok.matches(TT_KEYWORD, 'sea'):
            res.register(self.advance())
            
            # Check to make sure following token is an indentifier
            print(self.current_tok)
            if self.current_tok != TT_IDENTIFIER:
                return res.failure(SintaxisInvalidoError(
                    self.current_tok.pos_start, self.current_tok.pos_end, 'Expected indentifier'))
            
            # Assigns the variable name
            var_name = self.current_tok
            res.register(self.advance())

            # Check to ensure that following a var name is an =
            if self.current_tok.type != TT_EQ:
                return res.failure(SintaxisInvalidoError(
                    self.current_tok.pos_start, self.current_tok.pos_end, "Expected '='"))
            
            # Assign a new expression to the created variable
            res.register(self.advance())
            expr = res.register(self.expr())
            if res.error: return res
            return res.success(VarAssignNode(var_name, expr))

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

global_symbole_table = SymbolTable()
global_symbole_table.set("null", Number(0))

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
    context.symbol_table = global_symbole_table
    result = interpreter.visit(ast.node, context)
    return result.value, result.errorfrom .parser import run

RED = '\033[91m'
GREEN = '\033[92m'
GREY = '\033[90m'
BOLD = '\033[1m'
RESET = '\033[0m'
TITLE    = f"{BOLD}{RED}"
SUBTITLE = f"{GREEN}"
PROMPT   = f"{RED}mariachi {GREEN}> {RESET}"

def repl():
    print(f"{TITLE}Saludos desde el Mariachi REPL!{RESET}")
    print(f"{SUBTITLE}Type 'salir()' to quit.{RESET}\n")
    while True:
        code = input(PROMPT)
        if code == "salir()":
            break
        elif not code:
            continue
        
        result, error = run('repl', code)

        if error:
            print(error.as_string())
        else:
            print(result)

if __name__ == "__main__":
    repl()class ParseResult:
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
    
class RTResult:
    """A class for handling the results of runtime."""
    def __init__(self):
        self.value = None
        self.error = None

    def register(self, res):
        if res.error:
            self.error = res.error
        return res.value

    def success(self, value):
        self.value = value
        return self

    def failure(self, error):
        self.error = error
        return selfimport string

#################################
# CONSTANTS
#################################

DIGITS = '0123456789'
LETTERS = string.ascii_letters
LETTERS_DIGITS = LETTERS + DIGITS

KEYWORDS = [
    'sea' # let keyword, means "let it be"
    ]

#################################
# TOKENS
#################################

TT_INT = 'TT_INT'
TT_FLOAT = 'FLOAT'
TT_IDENTIFIER = 'IDENTIFIER'
TT_KEYWORD = 'KEYWORD'
TT_PLUS = 'PLUS'
TT_MINUS = 'MINUS'
TT_MUL = 'MUL'
TT_DIV = 'DIV'
TT_POW = 'POW'
TT_EQ = 'EQ'
TT_LPAREN = 'LPAREN'
TT_RPAREN = 'RPAREN'
TT_EOF = 'EOF'

class Token:
    """The tokens represented in the Mariachi Lang."""
    def __init__(self, type_, value=None, pos_start=None, pos_end=None):
        """Initial parameters for tokens, each one has a type and value."""
        self.type = type_
        self.value = value

        if pos_start:
            self.pos_start = pos_start.copy()
            self.pos_end = pos_start.copy()
            self.pos_end.advance()

        if pos_end:
            self.pos_end = pos_end.copy()

    def matches(self, type_, value):
        """Function to check if a token matches the current type and value."""
        return self.type == type_ and self.value == value

    def __repr__(self):
        """Representation method for printing to terminal window."""
        # If the token has a value both the type and value are returned
        if self.value:
            return f'{self.type}:{self.value}'
        # Otherwise just the type is returned
        return f'{self.type}'
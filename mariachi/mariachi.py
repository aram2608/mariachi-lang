from .values import *
from .lexer import *
from .parser import *
from .interpreter import *

global_symbol_table = SymbolTable()
global_symbol_table.set("nada", Number.null)
global_symbol_table.set("cierto", Number.true)
global_symbol_table.set("falso", Number.false)
global_symbol_table.set("canta", BuiltInFunction.print)

def run(fn, code, symbol_table=None):
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
    context = Context("<programma>")

    context.symbol_table = global_symbol_table
    result = interpreter.visit(ast.node, context)
    return result.value, result.error

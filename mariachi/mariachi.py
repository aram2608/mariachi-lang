from .numbers import *
from .lexer import *
from .parser import *

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
    context = Context('<programma>')

    # Declares a fresh symbol table each run time
    if symbol_table == None:
        symbol_table = SymbolTable()

    context.symbol_table = symbol_table
    result = interpreter.visit(ast.node, context)
    return result.value, result.error
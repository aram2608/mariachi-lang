from .values import *
from .lexer import *
from .parser import *
from .interpreter import *

global_symbol_table = SymbolTable()
global_symbol_table.set("nada", Number.null)
global_symbol_table.set("cierto", Number.true)
global_symbol_table.set("falso", Number.false)
global_symbol_table.set("canta", BuiltInFunction.canta)
global_symbol_table.set("eco", BuiltInFunction.eco)
global_symbol_table.set("escucha", BuiltInFunction.escucha)
global_symbol_table.set("escucha_num",BuiltInFunction.escucha_num)
global_symbol_table.set("limpia", BuiltInFunction.limpia)
global_symbol_table.set("es_num", BuiltInFunction.es_num)
global_symbol_table.set("es_texto", BuiltInFunction.es_texto)
global_symbol_table.set("es_lista", BuiltInFunction.es_lista)
global_symbol_table.set("es_funcion", BuiltInFunction.es_funcion)
global_symbol_table.set("pon", BuiltInFunction.pon)
global_symbol_table.set("roba", BuiltInFunction.roba)
global_symbol_table.set("extiende",  BuiltInFunction.extiende)

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

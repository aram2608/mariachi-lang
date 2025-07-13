# tests/test_core.py

from mariachi.mariachi import run, SymbolTable, Context, Number, BlockNode, IfNode
import math

# All return objects are returned as a custom List type,
# Need to find a way to compare for tests

def run_mariachi(code, symbol_table):
    value, error = run("<test>", code, symbol_table=symbol_table)
    assert error is None
    if hasattr(value, 'elements'):
        return value.elements[0]
    return value

def test_addition(fresh_table):
    assert run_mariachi("1 + 2", fresh_table) == 3

def test_subtraction(fresh_table):
    assert run_mariachi("5 - 3", fresh_table) == 2

def test_multiplication(fresh_table):
    assert run_mariachi("4 * 2", fresh_table) == 8

def test_division(fresh_table):
    assert run_mariachi("10 / 2", fresh_table) == 5

def test_power(fresh_table):
    assert run_mariachi("2 ** 3", fresh_table) == 8

def test_modulo(fresh_table):
    assert run_mariachi("10 % 3", fresh_table) == 1

def test_floordiv(fresh_table):
    assert run_mariachi("10 // 3", fresh_table) == 3

def test_equals(fresh_table):
    assert run_mariachi("2 == 2", fresh_table) == 1
    assert run_mariachi("2 == 3", fresh_table) == 0

def test_not_equals(fresh_table):
    assert run_mariachi("2 != 3", fresh_table) == 1
    assert run_mariachi("2 != 2", fresh_table) == 0

def test_comparisons(fresh_table):
    assert run_mariachi("2 < 3", fresh_table) == 1
    assert run_mariachi("3 <= 3", fresh_table) == 1
    assert run_mariachi("4 > 2", fresh_table) == 1
    assert run_mariachi("4 >= 5", fresh_table) == 0

def test_logical_ops(fresh_table):
    assert run_mariachi("1 y 0", fresh_table) == 0
    assert run_mariachi("1 o 0", fresh_table) == 1
    assert run_mariachi("jamas 0", fresh_table) == 1
    assert run_mariachi("jamas 1", fresh_table) == 0

def test_variable_assign(fresh_table):
    run_mariachi("sea x = 7", fresh_table)
    assert run_mariachi("x + 3", fresh_table) == 10

def test_variable_access(fresh_table):
    run_mariachi("sea x = 7", fresh_table)
    assert run_mariachi("x", fresh_table) == 7

def test_loop_for(fresh_table):
    run('programma',"sea r = 1", fresh_table)
    run('programma',"para i = 1 hasta 6 pues sea r = r * i", fresh_table)
    assert run_mariachi("r", fresh_table) == 120

def test_if(fresh_table):
    run('programma',"sea r = 1", fresh_table)
    run('programma', 'si r == 1 pues sea r = r + 1', fresh_table)
    assert run_mariachi("r", fresh_table) == 2

def test_constants(fresh_table):
    run_mariachi("fija PI = 3.14", fresh_table)
    result = run_mariachi("PI + 1", fresh_table)
    assert math.isclose(result, 4.14, rel_tol=1e-9)

def test_const_overwrite():
    symbol_table = SymbolTable()
    context = Context('test')
    context.symbol_table = symbol_table

    x = Number(4).set_context(context)
    symbol_table.set('x', x)

    try:
        symbol_table.set_const('x', Number(10).set_context(context))
    except Exception as e:
        assert str(e) == "'x' ya está definido y no se puede redefinir como constante"

def test_function_declaration(fresh_table):
    run('programma', "define hola(x) { x + 1 }", fresh_table)
    result, error = run('programma', "hola(2)", fresh_table)
    assert result.value == 3

def test_string(fresh_table):
    result = run_mariachi('"this is a string"', fresh_table)
    run_mariachi('sea x = "this is a string"', fresh_table)
    result_2 = run_mariachi("x", fresh_table)
    assert result == 'this is a string'
    assert result_2 == 'this is a string'

#def test_list_manipulation(fresh_table): ---> not possible yet as I need to figure out how to test a class instance version of our list
#    result, error = run('programma', '[1,2,3,4] * [1,2,3]', fresh_table)
#    result_2, error = run('programma', '[1,2,3,4] / 0', fresh_table)
#    result_3, error = run('programma', '[1,2,3] + 4', fresh_table)
#    assert result.elements == [1, 2, 3, 4, 1, 2, 3]
#    assert result_2.elements == 1
#    assert result_3.elements == [1, 2, 3, 4]

def test_builtins(fresh_table):
    #assert run_mariachi('canta("x")', fresh_table) == 'x' print returns 0 for some reason
    assert run_mariachi('eco("x")', fresh_table) == 'x'

def test_if_else_pos_end(fresh_table):
    # Create a mock IfNode with else_case
    result = run_mariachi("si 2 == 1 { canta(1) } sino { canta(0) }", fresh_table)
    print(result)
# tests/test_core.py

from mariachi.mariachi import run, SymbolTable, Context, Number, String, List
import math

def run_mariachi(code, symbol_table):
    value, error = run("<test>", code, symbol_table=symbol_table)
    assert error is None
    if hasattr(value, 'elements'):
        return value.elements[0]
    return value

def test_addition(fresh_table):
    assert run_mariachi("1 + 2", fresh_table)  == Number(3)

def test_subtraction(fresh_table):
    assert run_mariachi("5 - 3", fresh_table) == Number(2)

def test_multiplication(fresh_table):
    assert run_mariachi("4 * 2", fresh_table) == Number(8)

def test_division(fresh_table):
    assert run_mariachi("10 / 2", fresh_table) == Number(5)

def test_power(fresh_table):
    assert run_mariachi("2 ** 3", fresh_table) == Number(8)

def test_modulo(fresh_table):
    assert run_mariachi("10 % 3", fresh_table) == Number(1)

def test_floordiv(fresh_table):
    assert run_mariachi("10 // 3", fresh_table) == Number(3)

def test_equals(fresh_table):
    assert run_mariachi("2 == 2", fresh_table) == Number(1)
    assert run_mariachi("2 == 3", fresh_table) == Number(0)

def test_not_equals(fresh_table):
    assert run_mariachi("2 != 3", fresh_table) == Number(1)
    assert run_mariachi("2 != 2", fresh_table) == Number(0)

def test_comparisons(fresh_table):
    assert run_mariachi("2 < 3", fresh_table) == Number(1)
    assert run_mariachi("3 <= 3", fresh_table) == Number(1)
    assert run_mariachi("4 > 2", fresh_table) == Number(1)
    assert run_mariachi("4 >= 5", fresh_table) == Number(0)

def test_logical_ops(fresh_table):
    assert run_mariachi("1 y 0", fresh_table) == Number(0)
    assert run_mariachi("1 o 0", fresh_table) == Number(1)
    assert run_mariachi("jamas 0", fresh_table) == Number(1)
    assert run_mariachi("jamas 1", fresh_table) == Number(0)

def test_variable_assign(fresh_table):
    run_mariachi("sea x = 7", fresh_table)
    assert run_mariachi("x + 3", fresh_table) == Number(10)

def test_variable_access(fresh_table):
    run_mariachi("sea x = 7", fresh_table)
    assert run_mariachi("x", fresh_table) == Number(7)

def test_loop_for(fresh_table):
    run('programma',"sea r = 1", fresh_table)
    run('programma',"para i = 1 hasta 6 { sea r = r * i }", fresh_table)
    assert run_mariachi("r", fresh_table) == Number(120)

def test_if(fresh_table):
    run('programma',"sea r = 1", fresh_table)
    run('programma', 'si r == 1 pues sea r = r + 1', fresh_table)
    assert run_mariachi("r", fresh_table) == Number(2)

def test_constants(fresh_table):
    run_mariachi("fija PI = 3.14", fresh_table)
    result = run_mariachi("PI + 1", fresh_table)
    assert math.isclose(result.value, 4.14, rel_tol=1e-9)

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
    result = run('programma', "hola(2)", fresh_table)
    result = result[0]
    result = result.elements
    result = result[0]
    assert result == Number(3)

def test_string(fresh_table):
    run_mariachi('"this is a string"', fresh_table)
    run_mariachi('sea x = "this is a string"', fresh_table)
    assert run_mariachi('"this is a string"', fresh_table) == String('this is a string')
    assert run_mariachi("x", fresh_table) == String('this is a string')

def test_list_manipulation(fresh_table):
    result = run('programma', '[1,2,3,4] * [1,2,3]', fresh_table)
    result_2 = run('programma', '[1,2,3,4] / 0', fresh_table)
    result_3 = run('programma', '[1,2,3] + 4', fresh_table)
    result = [value.value for value in result[0].elements[0].elements]
    result_3 = [value.value for value in result_3[0].elements[0].elements]
    assert result == [1, 2, 3, 4, 1, 2, 3]
    assert result_2[0].elements[0].value == 1
    assert result_3 == [1, 2, 3, 4]

def test_builtins(fresh_table):
    assert run_mariachi('eco("x")', fresh_table) == String('x')

def test_if_else(fresh_table):
    assert run_mariachi("si 2 == 1 { eco(1) } sino { eco(0) }", fresh_table) == String('0')

def test_if(fresh_table):
    assert run_mariachi("si 1 == 1 { eco(1) }", fresh_table) == String('1')
# tests/test_if_else.py

from mariachi.mariachi import run

def run_mariachi(code, symbol_table):
    value, error = run("<test>", code, symbol_table=symbol_table)
    assert error is None
    if hasattr(value, 'elements'):
        return value.elements[0]
    return value

def test_if(fresh_table):
    result = run_mariachi("si 1 == 1 { canta(1) }", fresh_table)
    assert result == 0

def test_if_else_pos_end(fresh_table):
    # Create a mock IfNode with else_case
    result = run_mariachi("si 2 == 1 { canta(1) } sino { canta(0) }", fresh_table)
    assert result == 0
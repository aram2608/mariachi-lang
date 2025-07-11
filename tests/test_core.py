# tests/test_core.py

from mariachi.mariachi import run

def run_mariachi(code):
    value, error = run("<test>", code)
    assert error is None
    return value.value if value else None


def test_addition():
    assert run_mariachi("1 + 2") == 3

def test_subtraction():
    assert run_mariachi("5 - 3") == 2

def test_multiplication():
    assert run_mariachi("4 * 2") == 8

def test_division():
    assert run_mariachi("10 / 2") == 5

def test_power():
    assert run_mariachi("2 ** 3") == 8

def test_modulo():
    assert run_mariachi("10 % 3") == 1

def test_floordiv():
    assert run_mariachi("10 // 3") == 3

def test_equals():
    assert run_mariachi("2 == 2") == 1
    assert run_mariachi("2 == 3") == 0

def test_not_equals():
    assert run_mariachi("2 != 3") == 1
    assert run_mariachi("2 != 2") == 0

def test_comparisons():
    assert run_mariachi("2 < 3") == 1
    assert run_mariachi("3 <= 3") == 1
    assert run_mariachi("4 > 2") == 1
    assert run_mariachi("4 >= 5") == 0

def test_logical_ops():
    assert run_mariachi("1 y 0") == 0
    assert run_mariachi("1 o 0") == 1
    assert run_mariachi("jamas 0") == 1
    assert run_mariachi("jamas 1") == 0

def test_variable_assign():
    run_mariachi("sea x = 7")
    assert run_mariachi("x + 3") == 10

def test_loop_for():
    run_mariachi("sea r = 1")
    run_mariachi("para i = 1 hasta 6 pues sea r = r * i")
    assert run_mariachi("r") == 120

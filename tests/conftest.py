# tests/conftest.py

import pytest
from mariachi.mariachi import SymbolTable, Number

@pytest.fixture
def fresh_table():
    """Provides a new, clean symbol table for each test."""
    table = SymbolTable()
    return table

from mariachi.core.scanner import Scanner
from mariachi.utils.tokens import Token, TokenType
from typing import List

def run_scanner(source: str) -> List[Token]:
    scanner = Scanner(source)
    toks = scanner.scan_tokens()
    return toks[0]

def test_math():
    assert run_scanner("+") == Token(TokenType.PLUS, "+")
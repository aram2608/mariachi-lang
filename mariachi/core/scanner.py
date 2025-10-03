from __future__ import annotations
from string import ascii_letters
from typing import List, Dict, Callable

from ..utils.tokens import Token, TokenType


class ScanningError(Exception):
    def __init__(self, line: int, message: str, value=None):
        """
        A custom class to catch errors during scanning of Mariachie Scripts/REPL input.
        Args:
            line is is the line number in which the error occured
            message is the error message to be printed to the stream
            value is the literal value associated with any given token
        """
        self.line = line
        self.message = message
        self.value = value
        super().__init__(f"[line {line}] Error: {message}")

    def __str__(self):
        """
        A custom string representation method for the ScanningError class,
        If we have a value we return the string with value appended, otherwise
        we return the line and message only
        """
        # Some ASCII escape characters to pretty up the output
        RED = "\033[91m"
        RESET = "\033[0m"
        if self.value is not None:
            return (
                f"{RED}[line {self.line}] Error: {self.message} -> {self.value}{RESET}"
            )
        return f"{RED}[line {self.line}] Error: {self.message}{RESET}"


class Scanner:
    def __init__(self, source: str):
        # The source code
        self.source = source
        # Current position in source file
        self.current = 0
        # The start position
        self.start: int | None = None
        # Line count
        self.line: int = 1
        # Empty list to store our tokens
        self.tokens: List[Token] = []
        # Members to test for strings and numbers
        self.alpha = ascii_letters + "_"
        self.numbers = "0123456789"
        self.keywords: Dict[str, Callable] = {
            "sea": TokenType.SEA,  # let
            "y": TokenType.Y,  # and
            "o": TokenType.O,  # or
            "si": TokenType.SI,  # if
            "sino": TokenType.SINO,  # else
            "mientras": TokenType.MIENTRAS,  # while
            "para": TokenType.PARA,  # for
            "define": TokenType.DEFINE,  # define functions
            "entrega": TokenType.ENTREGA,  # return
            "objeto": TokenType.OBJETO,  # class
            "cierto": TokenType.CIERTO,  # true
            "falso": TokenType.FALSO,  # false
            "este": TokenType.ESTE,  # this
            "canta": TokenType.CANTA,  # print
            "nada": TokenType.NADA,  # nil
            "super": TokenType.SUPER,
        }

    def scan_tokens(self) -> List[Token]:
        """Method to create tokens from source code."""
        # While we are not at the end of the file
        while not self.is_end():
            # We set our start position and scan for tokens
            self.start = self.current
            try:
                self.scan()
            except ScanningError as e:
                print(e)

        # At the end of scanning we add an EOF token
        self.tokens.append(Token(TokenType.EOF, "", None, self.line))
        return self.tokens

    def scan(self) -> None:
        """Main logic for creating tokens."""
        # We first advance forward, returning the character
        char: str = self.advance()
        # We then match the character against all our predefined token types
        match char:
            # We increment our line count on new lines
            case "\n":
                self.line += 1
            # We skip empty characters
            case " " | "\r" | "\t":
                pass
            # Single character tokens
            case "*":
                self.add_token(TokenType.STAR)
            case "%":
                self.add_token(TokenType.MOD)
            case "?":
                self.add_token(TokenType.QUESTION)
            case '"':
                self.make_string()
            case "(":
                self.add_token(TokenType.LEFT_PAREN)
            case ")":
                self.add_token(TokenType.RIGHT_PAREN)
            case "{":
                self.add_token(TokenType.LEFT_BRACE)
            case "}":
                self.add_token(TokenType.RIGHT_BRACE)
            case ",":
                self.add_token(TokenType.COMMA)
            case ";":
                self.add_token(TokenType.SEMICOLON)
            case ":":
                self.add_token(TokenType.COLON)
            case ".":
                self.add_token(TokenType.DOT)
            # Double character tokens
            case "+":
                if self.match("+"):
                    self.add_token(TokenType.PLUS_PLUS)
                else:
                    self.add_token(TokenType.PLUS)
            case "-":
                if self.match("-"):
                    self.add_token(TokenType.MINUS_MINUS)
                else:
                    self.add_token(TokenType.MINUS)
            case "!":
                if self.match("="):
                    self.add_token(TokenType.BANG_EQUAL)
                else:
                    self.add_token(TokenType.BANG)
            case "=":
                if self.match("="):
                    self.add_token(TokenType.EQUAL_EQUAL)
                else:
                    self.add_token(TokenType.EQUAL)
            case "/":
                if self.match("/"):
                    self.make_comment()
                elif self.match("*"):
                    self.make_multiline_comment()
                else:
                    self.add_token(TokenType.SLASH)
            case ">":
                if self.match("="):
                    self.add_token(TokenType.GREATER_EQUAL)
                else:
                    self.add_token(TokenType.GREATER)
            case "<":
                if self.match("="):
                    self.add_token(TokenType.LESS_EQUAL)
                else:
                    self.add_token(TokenType.LESS)
            # We handle identifiers/numbers/keywords in our default case
            case _:
                # We first check for numbers
                if self.is_number(char):
                    self.make_number()
                # We can then check for identifiers/keywords
                elif self.is_alpha(char):
                    self.make_identifier()
                # Otherwise we kick out an error
                else:
                    raise ScanningError(
                        self.line,
                        "ScanningError: Unidentified token type.",
                    )

    def advance(self) -> str:
        """Helper method to return the current token and advance through the source."""
        # We store our current char
        chr: str = self.source[self.current]
        # We increment the current count and return the char
        self.current += 1
        return chr

    def add_token(self, _type: TokenType, literal: str | float | None = None) -> None:
        """This method extracts the lexeme and creates a new token."""
        # We first substring out the lexeme
        lex: str = self.source[self.start : self.current]
        # We can now add our token
        self.tokens.append(Token(_type, lex, literal, self.line))

    def make_identifier(self) -> None:
        """Helper method to make identifiers and keyword tokens."""
        # We continue so long as the current character is alpha numeric
        while self.is_alpha_num(self.peek()):
            self.advance()

        # We substring out the lexeme
        text: str = self.source[self.start : self.current]

        # We now need to test if the lexeme is inside the dictionary containing
        # our reserved keywords
        if text in self.keywords:
            # If so we use the lexeme as a key and return the TokenType of interest
            self.add_token(self.keywords[text])
        # Otherwise we create a new identifier
        else:
            self.add_token(TokenType.IDENTIFIER)

    def make_string(self) -> None:
        """Helper method to make strings."""
        # We continue to skip past characters as long as we have not reached
        # the end of the file or the closing ".
        while self.peek() != '"' and not self.is_end():
            # Lox allows multiline string
            if self.peek() == "\n":
                self.line += 1
            self.advance()
        # If we reach the end of the file we throw and error
        if self.is_end():
            raise ScanningError(
                line=self.line, message="ScanningError: Unterminated string"
            )

        # We can now jump across the closing "
        self.advance()

        # We then substring out the lexeme of interest and create out token
        string: str = self.source[self.start + 1 : self.current - 1]
        self.add_token(TokenType.STRING, string)

    def make_number(self) -> None:
        """Helper method to create number tokens"""
        # We continue so long as the current character is a number
        while self.is_digit(self.peek()):
            self.advance()

        # We leap over the decimal
        if self.peek() == "." and self.is_digit(self.peek_next()):
            self.advance()

            # We then continue so long as the current character is a number
            while self.is_digit(self.peek()):
                self.advance()

        # We collect the stubstring of the source code and add it as our token
        lex = self.source[self.start : self.current]
        self.add_token(TokenType.NUMBER, float(lex))

    def make_comment(self) -> None:
        """Helper method to create comments."""
        while self.peek() != "\n" and self.is_end():
            self.advance()

    def make_multiline_comment(self) -> None:
        """Helper method to create multiline comments."""
        # We store the position of the opening /*
        mlc_line: int = self.current
        # We run our loop so long as the file is not at the end
        while not self.is_end():
            # If we match a new line we increment the line number and advance
            if self.peek() == "\n":
                self.line += 1
                self.advance()
            # Once we reach the closing */ we can break out
            elif self.peek() == "*" and self.peek_next() == "/":
                self.advance()
                self.advance()
                return
            # Otherwise we skip forward
            else:
                self.advance()
        # If the comment is unterminated we throw and error
        raise ScanningError(mlc_line, "Unterminated multiline commennt")

    def peek(self) -> str:
        """Helper method to peek at current token."""
        # We simply index the source at our current position
        if self.is_end():
            return None
        return self.source[self.current]

    def peek_next(self) -> str:
        """Helper method to peek at the next token."""
        # We check if the next value is greater than the overall length of the source
        # If so we return a null terminator character
        if self.current + 1 >= len(self.source):
            return "\0"
        # If our check passes we return the next character
        return self.source[self.current + 1]

    def match(self, expected: str) -> bool:
        if self.is_end():
            return False

        if self.peek() != expected:
            return False

        self.current += 1
        return True

    def is_end(self) -> bool:
        """Helper method to check if we are past the end of the source code."""
        return self.current >= len(self.source)

    def is_alpha(self, char: str) -> bool:
        """Helper method to test if the current character is a letter."""
        if char == None:
            return False
        return char in self.alpha

    def is_number(self, char: str) -> bool:
        """Helper to test if a character is a number."""
        if char == None:
            return False
        return char in self.numbers

    def is_alpha_num(self, char: str) -> bool:
        """Helper to test if a character is alphanumeric."""
        return self.is_alpha(char) or self.is_number(char)

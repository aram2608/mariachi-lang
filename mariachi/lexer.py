"""The lexer module for the Mariachi Lang."""

from .token import *
from .errors import *
from .file_runner import *

class Lexer:
    def __init__(self, fn, text):
        # The input file name
        self.fn = fn
        # The processed text
        self.text = text
        # Tracks current position
        self.pos = Position(-1, 0, -1, fn, text)
        # Tracks current character, default is None type
        self.current_char = None
        self.advance()

    def advance(self):
        """A class method to increment position in text."""
        self.pos.advance(self.current_char)
        # Sets incremented character as the current character
        if self.pos.idx < len(self.text):
            self.current_char = self.text[self.pos.idx]
        else:
        # We need to set the current char back to None to prevent infinite loops
            self.current_char = None

    def make_tokens(self):
        """A class method to tokenize input text."""
        # Initialize an empty list to store the token
        tokens = []

        while self.current_char != None:
            if self.current_char in ' \t':
                self.advance()
            elif self.current_char in DIGITS:
                tokens.append(self.make_number())
            elif self.current_char == '+':
                tokens.append(Token(TT_PLUS, pos_start=self.pos))
                self.advance()
            elif self.current_char == '-':
                tokens.append(Token(TT_MINUS, pos_start=self.pos))
                self.advance()
            elif self.current_char == '*':
                tokens.append(Token(TT_MUL), pos_start=self.pos)
                self.advance()
            elif self.current_char == '/':
                tokens.append(Token(TT_DIV, pos_start=self.pos))
                self.advance()
            elif self.current_char == '(':
                tokens.append(Token(TT_LPAREN, pos_start=self.pos))
                self.advance()
            elif self.current_char == ')':
                tokens.append(Token(TT_RPAREN, pos_start=self.pos))
                self.advance()
            else:
                pos_start = self.pos.copy()
                char = self.current_char
                self.advance()
                # Returns no tokens and bad character error
                return [], InesperadoError(pos_start, self.pos, char)
        tokens.append(Token(TT_EOF, pos_start=self.pos))
        return tokens, None
    
    def make_number(self):
        """A class to handle tokenization of numbers."""
        # We handle all numbers as strings for tokenization.
        num_str = ''
        dot_count = 0
        pos_start = self.pos.copy()

        # The logic for handling integers vs floating point values.
        while self.current_char != None and self.current_char in DIGITS + '.':
            if self.current_char == '.':
                if dot_count == 1: 
                    break
                dot_count += 1
                num_str += '.'
            else:
                num_str += self.current_char
            self.advance()
        # Tokenization logic following evaluation of token type.
        if dot_count == 0:
            return Token(TT_INT, int(num_str), pos_start, self.pos)
        else:
            return Token(TT_FLOAT, float(num_str, pos_start, self.pos))
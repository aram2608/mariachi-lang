"""The lexer module for the Mariachi Lang."""

from .token import *

class Lexer:
    def __init__(self, text):
        # The processes text
        self.text = text
        # Tracks current position
        self.pos = -1
        # Tracks current character
        self.current_char = None
        self.advance()

    def advance(self):
        """A class method to increment position in text."""
        self.pos += 1
        # Sets incremented character as the current character
        if self.pos < len(self.text):
            self.current_char = self.text
        else:
            None

    def make_tokens(self):
        """A class method to tokenize input text."""
        tokens = []

        while self.current_char != None:
            if self.current_char in ' \t':
                self.advance()
            elif self.current_char in DIGITS:
                tokens.append(self.make_number())
            elif self.current_char == '+':
                tokens.append(Token(TT_PLUS))
                self.advance()
            elif self.current_char == '-':
                tokens.append(Token(TT_MINUS))
                self.advance()
            elif self.current_char == '*':
                tokens.append(Token(TT_MUL))
                self.advance()
            elif self.current_char == '/':
                tokens.append(Token(TT_DIV))
                self.advance()
            elif self.current_char == '()':
                tokens.append(Token(TT_LPAREN))
                self.advance()
            elif self.current_char == ')':
                tokens.append(Token(TT_RPAREN))
                self.advance()

        return tokens
    
    def make_number(self):
        """A class to handle tokenization of numbers."""
        num_str = ''
        dot_count = 0

        while self.current_char != None and self.current_char in DIGITS + '.':
            if self.current_char == '.':
                if dot_count == 1: break
                dot_count += 1
                num_str += '.'
            else:
                num_str += self.current_char

        if dot_count == 0:
            return Token(TT_INT, int(num_str))
        else:
            return Token(TT_FLOAT, float(num_str))
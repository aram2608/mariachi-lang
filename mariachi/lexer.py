from .token import *
from .errors import *

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

            # Ignore white spaces
            if self.current_char in ' \t':
                self.advance()

            # Tokenize numbers
            elif self.current_char in DIGITS:
                tokens.append(self.make_number())

            # Tokenize identifiers and keywords
            elif self.current_char in LETTERS:
                tokens.append(self.make_identifier())

            # Math operations
            elif self.current_char == '+':
                tokens.append(Token(TT_PLUS, pos_start=self.pos))
                self.advance()
            elif self.current_char == '-':
                pos_start = self.pos.copy()
                self.advance()
                if self.current_char == '>':
                    tokens.append(Token(TT_ARROW, pos_start=pos_start, pos_end=self.pos))
                    self.advance()
                else:
                    tokens.append(Token(TT_MINUS, pos_start=pos_start, pos_end=self.pos))
            elif self.current_char == '*':
                pos_start = self.pos.copy()
                self.advance()
                if self.current_char == '*':
                    tokens.append(Token(TT_POW, pos_start=pos_start, pos_end=self.pos))
                    self.advance()
                else:
                    tokens.append(Token(TT_MUL, pos_start=pos_start, pos_end=self.pos))
            elif self.current_char == '/':
                pos_start = self.pos.copy()
                self.advance()
                if self.current_char == '/':
                    tokens.append(Token(TT_FLOORDIV, pos_start=pos_start, pos_end=self.pos))
                    self.advance()
                else:
                    tokens.append(Token(TT_DIV, pos_start=pos_start, pos_end=self.pos))
            elif self.current_char == '%':
                tokens.append(Token(TT_MOD, pos_start=self.pos))
                self.advance()
            elif self.current_char == '(':
                tokens.append(Token(TT_LPAREN, pos_start=self.pos))
                self.advance()
            elif self.current_char == ')':
                tokens.append(Token(TT_RPAREN, pos_start=self.pos))
                self.advance()

            # Braces
            elif self.current_char == '{':
                tokens.append(Token(TT_LBRACE, pos_start=self.pos))
                self.advance()
            elif self.current_char == '}':
                tokens.append(Token(TT_RBRACE, pos_start=self.pos))
                self.advance()

            # Logical operations
            elif self.current_char == '!':
                token, error = self.make_not_equals()
                if error: return [], error
                tokens.append(token)
            elif self.current_char == '=':
                tokens.append(self.make_equals())
            elif self.current_char == '<':
                tokens.append(self.make_less_than())
            elif self.current_char == '>':
                tokens.append(self.make_greater_than())

            # Commas and comments
            elif self.current_char == ',':
                tokens.append(Token(TT_COMMA, pos_start=self.pos))
            elif self.current_char == '#':
                tokens.append(Token(TT_COMMENT, pos_start=self.pos))
            else:
                pos_start = self.pos.copy()
                char = self.current_char
                self.advance()
                # Returns no tokens and bad character error
                return [], InesperadoError(pos_start, self.pos, char)

        # End of file
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
            return Token(TT_FLOAT, float(num_str), pos_start, self.pos)
        
    def make_identifier(self):
        """A function to tokenize keywords and identifiers."""
        id_string = ''
        pos_start = self.pos.copy()

        while self.current_char != None and self.current_char in LETTERS_DIGITS + "_":
            id_string += self.current_char
            self.advance()

        tok_type = TT_KEYWORD if id_string in KEYWORDS else TT_IDENTIFIER
        return Token(tok_type, id_string, pos_start, self.pos)
    
    def make_not_equals(self):
        """A function to handle inequalities."""
        pos_start = self.pos.copy()
        self.advance()

        if self.current_char == '=':
            self.advance()
            return Token(TT_NE, pos_start=pos_start, pos_end=self.pos), None
        
        self.advance()
        return None, CaracterEsperadoError(pos_start, self.pos, "'=' despues de '!'")

    def make_equals(self):
        """A function to handle equalities."""
        tok_type = TT_EQ
        pos_start = self.pos.copy()
        self.advance()

        if self.current_char == '=':
            self.advance()
            tok_type = TT_EE
        return Token(tok_type, pos_start=pos_start, pos_end=self.pos)

    def make_less_than(self):
        """A function to handle equalities."""
        tok_type = TT_LT
        pos_start = self.pos.copy()
        self.advance()

        if self.current_char == '=':
            self.advance()
            tok_type = TT_LTE
        return Token(tok_type, pos_start=pos_start, pos_end=self.pos)
        
    def make_greater_than(self):
        """A function to handle equalities."""
        tok_type = TT_GT
        pos_start = self.pos.copy()
        self.advance()

        if self.current_char == '=':
            self.advance()
            tok_type = TT_GTE
        return Token(tok_type, pos_start=pos_start, pos_end=self.pos)
    
class Position:
    """A class to store the position of the different code attributes."""
    def __init__(self, idx, ln, col, fn, ftxt):
        """Initial parameters for the position class.
        Stores index, line, column, file name, and file text.
        """
        self.idx = idx
        self.ln = ln
        self.col = col
        self.fn = fn
        self.ftxt = ftxt

    def advance(self, current_char=None):
        """A function to advance through a file, line by line."""
        self.idx += 1
        self.col += 1
        # Checks for new lines
        if current_char == '\n':
            self.ln += 1
            self.col = 0

        return self
    
    def copy(self):
        """Copies all of the stored values at a given position."""
        return Position(self.idx, self.ln, self.col, self.fn, self.ftxt)
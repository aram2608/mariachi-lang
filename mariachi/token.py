"""Mariachi Lang token module."""

#################################
# CONSTANTS
#################################

DIGITS = '0123456789'

#################################
# TOKENS
#################################

TT_INT = 'TT_INT'
TT_FLOAT = 'FLOAT'
TT_PLUS = 'PLUS'
TT_MINUS = 'MINUS'
TT_MUL = 'MUL'
TT_DIV = 'DIV'
TT_LPAREN = 'LPAREN'
TT_RPAREN = 'RPAREN'

class Token:
    """The tokens represented in the Mariachi Lang."""
    def __init__(self, type_, value):
        """Initial parameters for tokens, each one has a type and value."""
        self.type = type_
        self.value = value

    def __repr__(self):
        """Representation method for printing to terminal window."""
        # If the token has a value both the type and value are returned
        if self.value: return f'{self.type}:{self.value}'
        # Otherwise just the type is returned
        return f'{self.type}'
import string

#################################
# CONSTANTS
#################################

DIGITS = '0123456789'
LETTERS = string.ascii_letters
LETTERS_DIGITS = LETTERS + DIGITS

KEYWORDS = [
    'sea',       # let
    'fija',      # const
    'y',         # and
    'o',         # or
    'jamas',     # not
    'cierto',    # true
    'nada',      # null or 0
    'falso',     # false
    'si',        # if
    'pues',      # then
    'quizas',    # elseif
    'sino',      # else
    'mientras',  # while
    'para',      # for
    'hasta',     # to
    'paso',      # step
    'anonimo',   # define an anonymous func

    'entrega',   # return
    'define',    # define
    'invoca',    # class creation
    'rompe',     # break
    'sigue',     # continue

    'baila',     # could be cool but dont know what it would do
    'canta',     # print
]

#################################
# TOKENS
#################################

TT_INT = 'INT'
TT_FLOAT = 'FLOAT'
TT_IDENTIFIER = 'IDENTIFIER'
TT_KEYWORD = 'KEYWORD'
TT_PLUS = 'PLUS'
TT_MINUS = 'MINUS'
TT_MUL = 'MUL'
TT_DIV = 'DIV'
TT_MOD = 'MOD'
TT_FLOORDIV = 'FLOORDIV'
TT_POW = 'POW'
TT_EQ = 'EQ'
TT_EE = 'EE'
TT_NE = 'NE'
TT_LT = 'LT'
TT_GT = 'GT'
TT_LTE = 'LTE'
TT_GTE = 'GTE'
TT_LPAREN = 'LPAREN'
TT_RPAREN = 'RPAREN'
TT_LBRACE = 'LBRACE'
TT_RBRACE = 'RBRACE'
TT_COMMA = 'COMMA'
TT_ARROW = 'ARROW'
TT_COMMENT = 'COMMENT'
TT_EOF = 'EOF'

class Token:
    """The tokens represented in the Mariachi Lang."""
    def __init__(self, type_, value=None, pos_start=None, pos_end=None):
        """Initial parameters for tokens, each one has a type and value."""
        self.type = type_
        self.value = value

        if pos_start:
            self.pos_start = pos_start.copy()
            self.pos_end = pos_start.copy()
            self.pos_end.advance()

        if pos_end:
            self.pos_end = pos_end.copy()

    def matches(self, type_, value):
        """Function to check if a token matches the current type and value."""
        return self.type == type_ and self.value == value

    def __repr__(self):
        """Representation method for printing to terminal window."""
        # If the token has a value both the type and value are returned
        if self.value:
            return f'{self.type}:{self.value}'
        # Otherwise just the type is returned
        return f'{self.type}'
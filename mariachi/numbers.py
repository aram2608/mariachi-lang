from .errors import *

class Number:
    """Class for defining arithmetic logic."""
    def __init__(self, value):
        self.value = value
        self.set_position()
        self.set_context()

    def set_position(self, pos_start=None, pos_end=None):
        """Sets positions for error tracking."""
        self.pos_start = pos_start
        self.pos_end = pos_end
        return self
    
    def added_to(self, other):
        """A function to represent addition."""
        if isinstance(other, Number):
            return Number(self.value + other.value).set_context(self.context), None
        
    def subbed_by(self, other):
        """A function to represent subtraction."""
        if isinstance(other, Number):
            return Number(self.value - other.value).set_context(self.context), None
        
    def multed_by(self, other):
        """A function to represent multiplication."""
        if isinstance(other, Number):
            return Number(self.value * other.value).set_context(self.context), None
        
    def divided_by(self, other):
        """A function to represent division."""
        if isinstance(other, Number):
            if other.value == 0:
                return None, EjecucionError(
                    other.pos_start, other.pos_end, 'Division por zero',
                    self.context
                )
            return Number(self.value / other.value).set_context(self.context), None
        
    def power_by(self, other):
        """A function to represent power multiplication."""
        if isinstance(other, Number):
            return Number(self.value ** other.value).set_context(self.context), None
        
    def modulo_by(self, other):
        """A function to represent modulo operations."""
        if isinstance(other, Number):
            if other.value == 0:
                return None, EjecucionError(
                    other.pos_start, other.pos_end, 'Division por zero',
                    self.context
                )
            return Number(self.value % other.value).set_context(self.context), None
        
    def floordiv_by(self, other):
        """A function to represent floor division."""
        if isinstance(other, Number):
            if other.value == 0:
                return None, EjecucionError(
                    other.pos_start, other.pos_end, 'Division por zero', self.context
                )
        return Number(self.value // other.value).set_context(self.context), None
    
    def get_comparison_eq(self, other):
        """Handles equals comparisons."""
        if isinstance(other, Number):
            return Number(int(self.value == other.value)).set_context(self.context), None

    def get_comparison_lt(self, other):
        """Less than comparisons."""
        if isinstance(other, Number):
            return Number(int(self.value < other.value)).set_context(self.context), None

    def get_comparison_lte(self, other):
        """Less than or equal to comparisons."""
        if isinstance(other, Number):
            return Number(int(self.value <= other.value)).set_context(self.context), None

    def get_comparison_gt(self, other):
        """Greater than comparisons."""
        if isinstance(other, Number):
            return Number(int(self.value > other.value)).set_context(self.context), None

    def get_comparison_gte(self, other):
        """Greater than or equal to comparisons."""
        if isinstance(other, Number):
            return Number(int(self.value >= other.value)).set_context(self.context), None

    def anded_by(self, other):
        if isinstance(other, Number):
            return Number(int(self.value and other.value)).set_context(self.context), None

    def ored_by(self, other):
        if isinstance(other, Number):
            return Number(int(self.value or other.value)).set_context(self.context), None
        
    def notted(self):
        return Number(1 if self.value == 0 else 0).set_context(self.context), None
    
    def is_true(self):
        return self.value != 0

    def copy(self):
        """A function to copy an operations position."""
        copy = Number(self.value)
        copy.set_position(self.pos_start, self.pos_end)
        copy.set_context(self.context)
        return copy
        
    def set_context(self, context=None):
        self.context = context
        return self
        
    def __repr__(self):
        return str(self.value)
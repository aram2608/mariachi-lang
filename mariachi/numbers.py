"""Module for arithmetic operations."""

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
        if isinstance(other, Number):
            return Number(self.value + other.value).set_context(self.context), None
        
    def subbed_by(self, other):
        if isinstance(other, Number):
            return Number(self.value - other.value).set_context(self.context), None
        
    def multed_by(self, other):
        if isinstance(other, Number):
            return Number(self.value * other.value).set_context(self.context), None
        
    def divided_by(self, other):
        if isinstance(other, Number):
            if other.value == 0:
                return None, EjecucionError(
                    other.pos_start, other.pos_end, 'Division por zero',
                    self.context
                )
            return Number(self.value / other.value).set_context(self.context), None
        
    def power_by(self, other):
        if isinstance(other, Number):
            return Number(self.value ** other.value).set_context(self.set_context), None
        
    def set_context(self, context=None):
        self.context = context
        return self
        
    def __repr__(self):
        return str(self.value)
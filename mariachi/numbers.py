"""Module for arithmetic operations."""

from .errors import *

class Number:
    """Class for defining arithmetic logic."""
    def __init__(self, value):
        self.value = value
        self.set_position()

    def set_position(self, pos_start=None, pos_end=None):
        """Sets positions for error tracking."""
        self.pos_start = pos_start
        self.pos_end = pos_end
        return self
    
    def added_to(self, other):
        if isinstance(other, Number):
            return Number(self.value + other.value), None
        
    def subbed_by(self, other):
        if isinstance(other, Number):
            return Number(self.value - other.value), None
        
    def multed_by(self, other):
        if isinstance(other, Number):
            return Number(self.value * other.value), None
        
    def divided_by(self, other):
        if isinstance(other, Number):
            if other.value == 0:
                return None, EjecucionError(
                    other.pos_start, other.pos_end, 'Division por zero'
                )
            return Number(self.value / other.value), None
        
    def __repr__(self):
        return str(self.value)
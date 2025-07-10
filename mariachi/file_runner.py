
class Position:
    def __init__(self, idx, ln, col, fn, ftxt):
        """Initial parameters for the position class.
        Stores index, line, column, file name, and file text.
        """
        self.idx = idx
        self.ln = ln
        self.col = col
        self.fn = fn
        self.ftxt = ftxt

    def advance_position(self, current_char):
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
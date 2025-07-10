"""Custom error module for the Mariachi Lang."""

class Error:
    def __init__(self, pos_start, pos_end, error_name, details):
        self.pos_start = pos_start
        self.pos_end = pos_end
        self.error_name = error_name
        self.details = details

    def as_string(self):
        """Converts our error type into a string with provided details."""
        result = f'{self.error_name}: {self.details}'
        result += f'\nFile {self.pos_start.fn} line {self.pos_end.ln} + 1'
        return result
    
class InesperadoError(Error):
    def __init__(self, pos_start, pos_end, details):
        """Subclass for unexpected character inputs."""
        super().__init__(pos_start, pos_end, 'Caracter Inesperado', details)
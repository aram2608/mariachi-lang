"""Custom error module for the Mariachi Lang."""

class Error:
    def __init__(self, error_name, details):
        self.error_name = error_name
        self.details = details

    def as_string(self):
        """Converts our error type into a string with provided details."""
        result = f'{self.error_name}: {self.details}'
        return result
    
class InesperadoError(Error):
    def __init__(self, details):
        """Subclass for unexpected character inputs."""
        super().__init__('Caracter Inesperado', details)
"""Custom error module for the Mariachi Lang."""

class Errors:
    def __init__(self, error_name, details):
        self.error_name = error_name
        self.details = details

    def as_string(self):
        result = f'{self.error_name}:{self.details}'
        return result
    
    
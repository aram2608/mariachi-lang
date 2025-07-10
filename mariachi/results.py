class ParseResult:
    """A class for handling the results from parsing."""
    def __init__(self):
        self.error = None
        self.node = None

    def register(self, res):
        """Checks for errors."""
        if isinstance(res, ParseResult):
            if res.error:
                self.error = res.error
            return res.node
        return res

    def success(self, node):
        self.node = node
        return self

    def failure(self, error):
        self.error = error
        return self
    
class RTResult:
    """A class for handling the results of runtime."""
    def __init__(self):
        self.value = None
        self.error = None

    def register(self, res):
        if res.error:
            self.error = res.error
        return res.value

    def success(self, value):
        self.value = value
        return self

    def failure(self, error):
        self.error = error
        return self
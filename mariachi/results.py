class ParseResult:
    """A class for handling the results from parsing."""

    def __init__(self):
        self.error = None
        self.node = None
        self.last_registered_advance_count = 0
        self.advance_count = 0

    def register_advancement(self):
        """A function to keep track of advancements."""
        self.last_registered_advance_count = 1
        self.advance_count += 1

    def register(self, res):
        """A function to pass parse results."""
        self.last_registered_advance_count = res.advance_count
        self.advance_count += res.advance_count
        if res.error:
            self.error = res.error
        return res.node

    def success(self, node):
        """A function to declare succesful parsing."""
        self.node = node
        return self

    def failure(self, error):
        """A function to declare unsuccessful parsing."""
        if not self.error or self.advance_count == 0:
            self.error = error
        return self


class RTResult:
    """A class for handling the results of runtime."""

    def __init__(self):
        self.value = None
        self.error = None

    def register(self, res):
        """A function to pass Runtime Results."""
        if res.error:
            self.error = res.error
        return res.value

    def success(self, value):
        """A function to return succesful runtime results."""
        self.value = value
        return self

    def failure(self, error):
        """A function to return unsuccesful runtime results."""
        self.error = error
        return self

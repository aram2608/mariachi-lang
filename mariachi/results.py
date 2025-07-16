class ParseResult:
    """A class for handling the results from parsing."""

    def __init__(self):
        self.error = None
        self.node = None
        self.last_registered_advance_count = 0
        self.advance_count = 0
        self.to_reverse_count = 0

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

    def try_register(self, res):
        if res.error:
            self.to_reverse_count = res.advance_count
            return None
        return self.register(res)

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
        self.reset()

    def reset(self):
        """reset initialized parameters."""
        self.value = None
        self.error = None
        self.func_return_value = None
        self.loop_should_break = False
        self.loop_should_continue = False

    def register(self, res):
        """A function to pass Runtime Results."""
        if res.error:
            self.error = res.error
        self.func_return_value = res.func_return_value
        self.loop_should_break = res.loop_should_break
        self.loop_should_continue = res.loop_should_continue
        return res.value

    def success(self, value):
        """A function to return succesful runtime results."""
        self.reset()
        self.value = value
        return self

    def success_return(self, value):
        self.reset()
        self.func_return_value = value
        return self

    def success_continue(self):
        self.reset()
        self.loop_should_continue = True
        return self

    def success_break(self):
        self.reset()
        self.loop_should_break = True
        return self

    def failure(self, error):
        """A function to return unsuccesful runtime results."""
        self.reset()
        self.error = error
        return self

    def should_return(self):
        return (
            self.error
            or self.func_return_value
            or self.loop_should_break
            or self.loop_should_continue
        )

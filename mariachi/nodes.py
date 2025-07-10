class NumberNode:
    def __init__(self, tok):
        self.tok = tok
    
    def __repr__(self):
        """A custom representation method for our number node."""
        return f'{self.tok}'
    
class BindingOperatorNode:
    def __init__(self, left_node, tok, right_node):
        self.left_node = left_node
        self.tok = tok
        self.right_node = right_node

    def __repr__(self):
        return f'{self.left_node}, {self.tok}, {self.right_node}'

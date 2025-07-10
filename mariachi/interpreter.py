"""The interpreter module for the Mariachi Lang toy language."""

class Interpreter:
    """The interpreter for the Mariachi Lang toy language."""
    def visit(self, node):
        # Creates method name from the node classes
        method_name = f'visit_{type(node).__name__}'
        # The get attribute method returns a named attribute from an object
        method = getattr(self, method_name, self.no_visit_method)
        return method(node)
    
    def no_visit_method(self,node):
        raise Exception(f'No visit_{type(node).__name__} method defined.')
    
    def visit_NumberNode(self, node):
        print("Found num node")

    def visit_BinaryOpNode(self, node):
        print('Found bin op node')
        self.visit(node.left_node)
        self.visit(node.right_node)

    def visit_UnaryOpNode(self, node):
        print("Found unary op node.")
        self.visit(node.node)
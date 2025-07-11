class NumberNode:
    def __init__(self, tok):
        self.tok = tok
        self.pos_start = self.tok.pos_start
        self.pos_end = self.tok.pos_end
    
    def __repr__(self):
        """A custom representation method for our number node."""
        return f'{self.tok}'
    
class BinaryOpNode:
    """Node class for binary operations."""
    def __init__(self, left_node, op_tok, right_node):
        self.left_node = left_node
        self.op_tok = op_tok
        self.right_node = right_node
        self.pos_start = self.left_node.pos_start
        self.pos_end = self.right_node.pos_end

    def __repr__(self):
        return f'({self.left_node}, {self.op_tok}, {self.right_node})'
    
class UnaryOpNode:
    """Node class for unary operations."""
    def __init__(self, op_tok, node):
        self.op_tok = op_tok
        self.node = node
        self.pos_start = self.op_tok.pos_start
        self.pos_end = node.pos_end

    def __repr__(self):
        """Custom representation method."""
        return f'({self.op_tok}, {self.node})'
    
class VarAssignNode:
    def __init__(self, var_name_tok, value_node):
        self.var_name_tok = var_name_tok
        self.value_node = value_node

        self.pos_start = self.value_node.pos_start
        self.pos_end = self.value_node.pos_end

class VarAccessNode:
    def __init__(self, var_name_tok):
        self.var_name_tok = var_name_tok

        self.pos_start = self.var_name_tok.pos_start
        self.pos_end = self.var_name_tok.pos_end

class PrintNode:
    def __init__(self, expr_node):
        self.expr_node = expr_node
        self.pos_start = expr_node.pos_start
        self.pos_end = expr_node.pos_end

    def __repr__(self):
        return f'(canta {self.expr_node})'
    
class IfNode:
    def __init__(self, cases, else_case):
        self.cases = cases
        self.else_case = else_case

        self.pos_start = self.cases[0][0].pos_start
        self.pos_end = (self.else_case or self.cases[len(self.cases) - 1][0]).pos_end

class BlockNode:
    def __init__(self, statements):
        self.statements = statements
        self.pos_start = statements[0].pos_start if statements else None
        self.pos_end = statements[-1].pos_end if statements else None

    def __repr__(self):
        return f'(bloque {self.statements})'

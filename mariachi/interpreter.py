"""The interpreter module for the Mariachi Lang toy language."""

from .numbers import *
from .token import *
from .results import *

class Interpreter:
    """The interpreter for the Mariachi Lang toy language."""
    def visit(self, node, context):
        # Creates method name from the node classes
        method_name = f'visit_{type(node).__name__}'
        # The get attribute method returns a named attribute from an object
        method = getattr(self, method_name, self.no_visit_method)
        return method(node, context)
    
    def no_visit_method(self, node, context):
        raise Exception(f'No visit_{type(node).__name__} method defined.')
    
    def visit_NumberNode(self, node, context):
        return RTResult().success(Number(node.tok.value).set_context(context).set_position(node.pos_start, node.pos_end))

    def visit_BinaryOpNode(self, node, context):
        res = RTResult()
        left = res.register(self.visit(node.left_node, context))
        if res.error:
            return res
        right = res.register(self.visit(node.right_node, context))
        if res.error:
            return res

        if node.op_tok.type == TT_PLUS:
            result, error = left.added_to(right)
        if node.op_tok.type == TT_MINUS:
            result, error = left.subbed_by(right)
        if node.op_tok.type == TT_MUL:
            result, error = left.multed_by(right)
        if node.op_tok.type == TT_DIV:
            result, error = left.divided_by(right)

        if error:
            return res.failure(error)
        return res.success(result.set_position(node.pos_start, node.pos_end))

    def visit_UnaryOpNode(self, node, context):
        res = RTResult()
        number = res.register(self.visit(node.node, context))
        if res.error:
            return res
        if node.op_tok.type == TT_MINUS:
            number, error = number.multed_by(Number(-1))

        if error:
            return res.failure(error)
        return res.success(number.set_position(node.pos_start, node.pos_end))
# Shelved ideas because they broke a bunch of stuff

# Print

class PrintNode:
    def __init__(self, expr_node):
        self.expr_node = expr_node
        self.pos_start = expr_node.pos_start
        self.pos_end = expr_node.pos_end

    def __repr__(self):
        return f'(canta {self.expr_node})'

    """
        # Print statement
        if self.current_tok.matches(TT_KEYWORD, 'canta'):
            res.register_advancement()
            self.advance()

            expr = res.register(self.expr())
            if res.error:
                return res
            return res.success(PrintNode(expr))
    """

class ConcatNode:
    def __init__(self, left_node, right_node):
        self.left_node = left_node
        self.right_node = right_node

    def visit_ConcatNode(self, node, context):
        res = RTResult()
        left = res.register(self.visit(node.left_node, context))
        if res.error: return res
        right = res.register(self.visit(node.right_node, context))
        if res.error: return res

        if isinstance(left, String) and isinstance(right, String):
            result, error = left.added_to(right)
            if error: return res.failure(error)
            return res.success(result.set_position(node.pos_start, node.pos_end))
        elif isinstance(left, List) and isinstance(right, List):
            result, error = left.concat_list(right)
            if error: return res.failure(error)
            return res.success(result.set_position(node.pos_start, node.pos_end))

KEYWORDS = [
    'anonimo',   # define an anonymous func

    'roba',      # retrieve an item from a list
    'borra',     # delete a list item
    'pon',       # add a list item
    'trenza',    # concatenate

    'entrega',   # return
    'define',    # define
    'invoca',    # class creation
    'rompe',     # break
    'sigue',     # continue

    'baila',     # could be cool but dont know what it would do
    'canta',     # print
    ]


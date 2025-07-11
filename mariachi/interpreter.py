from .numbers import *
from .token import *
from .results import *
from .context import *
from .errors import *

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
        return RTResult().success(Number(node.tok.value).with_meta(context, node.pos_start, node.pos_end))

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
        elif node.op_tok.type == TT_MINUS:
            result, error = left.subbed_by(right)
        elif node.op_tok.type == TT_MUL:
            result, error = left.multed_by(right)
        elif node.op_tok.type == TT_DIV:
            result, error = left.divided_by(right)
        elif node.op_tok.type == TT_POW:
            result, error = left.power_by(right)
        elif node.op_tok.type == TT_MOD:
            result, error = left.modulo_by(right)
        elif node.op_tok.type == TT_FLOORDIV:
            result, error = left.floordiv_by(right)
        elif node.op_tok.type == TT_NE:
            result, error = left.get_comparison_ne(right)
        elif node.op_tok.type == TT_EE:
            result, error = left.get_comparison_eq(right)
        elif node.op_tok.type == TT_LT:
            result, error = left.get_comparison_lt(right)
        elif node.op_tok.type == TT_LTE:
            result, error = left.get_comparison_lte(right)
        elif node.op_tok.type == TT_GT:
            result, error = left.get_comparison_gt(right)
        elif node.op_tok.type == TT_GTE:
            result, error = left.get_comparison_gte(right)
        elif node.op_tok.matches(TT_KEYWORD, 'y'):
            result, error = left.anded_by(right)
        elif node.op_tok.matches(TT_KEYWORD, 'o'):
            result, error = left.ored_by(right)
        else:
            return res.failure(EjecucionError(
                node.pos_start, node.pos_end,
                f"Operador desconocido '{node.op_tok}'",
                context
            ))

        if error:
            return res.failure(error)
        return res.success(result.set_position(node.pos_start, node.pos_end))

    def visit_UnaryOpNode(self, node, context):
        res = RTResult()
        number = res.register(self.visit(node.node, context))
        if res.error: return res

        error = None

        if node.op_tok.type == TT_MINUS:
            number, error = number.multed_by(Number(-1))
        elif node.op_tok.matches(TT_KEYWORD, 'jamas'):
            number, error = number.notted()

        if error:
            return res.failure(error)
        return res.success(number.set_position(node.pos_start, node.pos_end))
    
    def visit_VarAssignNode(self, node, context):
        res = RTResult()
        var_name = node.var_name_tok.value
        value = res.register(self.visit(node.value_node, context))
        if res.error: return res

        context.symbol_table.set(var_name, value)
        return res.success(value)

    def visit_VarAccessNode(self, node, context):
        res = RTResult()
        var_name = node.var_name_tok.value
        value = context.symbol_table.get(var_name)

        if not value:
            return res.failure(EjecucionError(
                node.pos_start, node.pos_end, f"'{var_name}' no es definido", context))
        value = value.copy().set_position(node.pos_start, node.pos_end)
        return res.success(value)
    
    def visit_ConstAssignNode(self, node, context):
        res = RTResult()
        name = node.const_name_tok.value
        value = res.register(self.visit(node.value_node, context))
        if res.error: return res

        try:
            context.symbol_table.set_const(name, value)
        except Exception as e:
            return res.failure(EjecucionError(
                node.pos_start, node.pos_end, str(e), context
            ))

        return res.success(value)
    
    def visit_ConstAccessNode(self, node, context):
        res = RTResult()
        var_name = node.var_name_tok.value
        value = context.symbol_table.get(var_name)

        if not value:
            return res.failure(EjecucionError(
                node.pos_start, node.pos_end, f"'{var_name}' no es definido", context))
        value = value.copy().set_position(node.pos_start, node.pos_end)
        return res.success(value)
    
    def visit_PrintNode(self, node, context):
        res = RTResult()
        value = res.register(self.visit(node.expr_node, context))
        if res.error: return res
        print(value)
        return res.success(Number(0))
    
    def visit_IfNode(self, node, context):
        res = RTResult()

        for condition, expr in node.cases:
            condition_value = res.register(self.visit(condition, context))
            if res.error: return res

            if condition_value.is_true():
                result = res.register(self.visit(expr, context))
                if res.error: return res
                return res.success(result)

        if node.else_case:
            result = res.register(self.visit(node.else_case, context))
            if res.error: return res
            return res.success(result)

        return res.success(None)

    def visit_BlockNode(self, node, context):
        res = RTResult()
        result = None

        for statement in node.statements:
            result = res.register(self.visit(statement, context))
            if res.error: return res

        # Return last statement's result
        return res.success(result or None)
    
    def visit_ForNode(self, node, context):
        res = RTResult()

        start_value = res.register(self.visit(node.start_value_node, context))
        if res.error: return res

        end_value = res.register(self.visit(node.end_value_node, context))
        if res.error: return res

        if node.step_value_node:
            step_value = res.register(self.visit(node.step_value_node, context))
            if res.error: return res
        else:
            step_value = Number(1)

        i = start_value.value

        if step_value.value >= 0:
            condition = lambda: i < end_value.value
        else:
            condition = lambda: i > end_value.value

        while condition():
            context.symbol_table.set(node.var_name_tok.value, Number(i))
            i += step_value.value

            res.register(self.visit(node.body_node, context))
            if res.error: return res
        return res.success(None)

    def visit_WhileNode(self, node, context):
        res = RTResult()
        while True:
            condition = res.register(self.visit(node.condition_node, context))
            if res.error: return res

            if not condition.is_true(): break

            res.register(self.visit(node.body_node, context))
            if res.error: return res
        return res.success(None)
    
class SymbolTable:
    def __init__(self):
        self.symbols = {}
        self.constants = {}
        self.parent = None

    def get(self, name):
        value = self.symbols.get(name)
        if value is None:
            value = self.constants.get(name)
        if value is None and self.parent:
            return self.parent.get(name)
        return value

    def set(self, name, value):
        if name in self.constants:
            raise Exception(f"'{name}' es una constante y no se puede cambiar")
        self.symbols[name] = value

    def set_const(self, name, value):
        if name in self.symbols or name in self.constants:
            raise Exception(f"'{name}' ya está definido y no se puede redefinir como constante")
        self.constants[name] = value

    def remove(self, name):
        if name in self.constants:
            raise Exception(f"'{name}' es una constante y no se puede borrar")
        del self.symbols[name]
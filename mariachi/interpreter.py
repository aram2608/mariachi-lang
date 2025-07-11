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
    
    def visit_FuncDefNode(self, node, context):
        res = RTResult()

        func_name = node.var_name_tok.value if node.var_name_tok else None
        body_node = node.body_node
        arg_name = [arg_name.value for arg_name in node.arg_name_toks]
        func_value = Function(func_name, body_node, arg_name).with_meta(context, node.pos_start, node.pos_end)

        if node.var_name_tok:
            context.symbol_table.set(func_name, func_value)

        return res.success(func_value)
    
    def visit_CallNode(self, node, context):
        res = RTResult()
        args = []

        value_to_call = res.register(self.visit(node.node_to_call, context))
        if res.error: return res

        value_to_call = value_to_call.copy().set_position(node.pos_start, node.pos_end)

        for arg_node in node.arg_nodes:
            args.append(res.register(self.visit(arg_node, context)))
            if res.error: return res

        return_value = res.register(value_to_call.execute(args))
        if res.error: return res
        return res.success(return_value)
    
    def visit_StringNode(self, node, context):
        return RTResult().success(
            String(node.tok.value).with_meta(context, node.pos_start, node.pos_end))
    
class SymbolTable:
    def __init__(self, parent=None):
        self.symbols = {}
        self.constants = {}
        self.parent = parent

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

class Value:
    def __init__(self):
        self.set_position()
        self.set_context()

    def set_position(self, pos_start=None, pos_end=None):
        self.pos_start = pos_start
        self.pos_end = pos_end
        return self

    def set_context(self, context=None):
        self.context = context
        return self

    def with_meta(self, context, pos_start, pos_end):
        """Wrapper function to get both positions and context."""
        return self.set_context(context).set_position(pos_start, pos_end)

    def added_to(self, other):
        return None, self.illegal_operation(other)

    def subbed_by(self, other):
        return None, self.illegal_operation(other)

    def multed_by(self, other):
        return None, self.illegal_operation(other)

    def divided_by(self, other):
        return None, self.illegal_operation(other)

    def power_by(self, other):
        return None, self.illegal_operation(other)

    def get_comparison_eq(self, other):
        return None, self.illegal_operation(other)

    def get_comparison_ne(self, other):
        return None, self.illegal_operation(other)

    def get_comparison_lt(self, other):
        return None, self.illegal_operation(other)

    def get_comparison_gt(self, other):
        return None, self.illegal_operation(other)

    def get_comparison_lte(self, other):
        return None, self.illegal_operation(other)

    def get_comparison_gte(self, other):
        return None, self.illegal_operation(other)

    def anded_by(self, other):
        return None, self.illegal_operation(other)

    def ored_by(self, other):
        return None, self.illegal_operation(other)

    def notted(self):
        return None, self.illegal_operation()

    def execute(self, args):
        return RTResult().failure(self.illegal_operation())

    def copy(self):
        raise Exception('No copy method defined')

    def is_true(self):
        return False

    def illegal_operation(self, other=None):
        if not other:
            other = self
        return EjecucionError(
            self.pos_start, other.pos_end,
            'Operación no permitida',
            self.context
        )
    
class Function(Value):
	def __init__(self, name, body_node, arg_names):
		super().__init__()
		self.name = name or "<anonimo>"
		self.body_node = body_node
		self.arg_names = arg_names

	def execute(self, args):

		res = RTResult()
		interpreter = Interpreter()

		new_context = Context(self.name, self.context, self.pos_start)
		new_context.symbol_table = SymbolTable(new_context.parent.symbol_table)

		if len(args) > len(self.arg_names):
			return res.failure(EjecucionError(
				self.pos_start, self.pos_end,
				f"{len(args) - len(self.arg_names)} demasiados argumentos pasados a '{self.name}'",
				self.context
			))

		if len(args) < len(self.arg_names):
			return res.failure(EjecucionError(
				self.pos_start, self.pos_end,
				f"{len(self.arg_names) - len(args)} no suficiente argumentos pasados a '{self.name}'",
				self.context
			))

		for i in range(len(args)):
			arg_name = self.arg_names[i]
			arg_value = args[i]
			arg_value.set_context(new_context)
			new_context.symbol_table.set(arg_name, arg_value)

		value = res.register(interpreter.visit(self.body_node, new_context))
		if res.error:
			return res

		return res.success(value)

	def copy(self):
		copy = Function(self.name, self.body_node, self.arg_names)
		copy.set_context(self.context)
		copy.set_position(self.pos_start, self.pos_end)
		return copy

	def __repr__(self):
		return f"<funcion {self.name}>"

class Number(Value):
    """Class for defining arithmetic logic."""
    def __init__(self, value):
        super().__init__()
        self.value = value
    
    def added_to(self, other):
        """A function to represent addition."""
        if isinstance(other, Number):
            return Number(self.value + other.value).set_context(self.context), None
        else:
            return None, self.illegal_operation(self, other)
        
    def subbed_by(self, other):
        """A function to represent subtraction."""
        if isinstance(other, Number):
            return Number(self.value - other.value).set_context(self.context), None
        else:
            return None, self.illegal_operation(self, other)
        
    def multed_by(self, other):
        """A function to represent multiplication."""
        if isinstance(other, Number):
            return Number(self.value * other.value).set_context(self.context), None
        else:
            return None, self.illegal_operation(self, other)
        
    def divided_by(self, other):
        """A function to represent division."""
        if isinstance(other, Number):
            if other.value == 0:
                return None, EjecucionError(
                    other.pos_start, other.pos_end, 'Division por zero',
                    self.context
                )
            return Number(self.value / other.value).set_context(self.context), None
        else:
            return None, self.illegal_operation(self, other)
        
    def power_by(self, other):
        """A function to represent power multiplication."""
        if isinstance(other, Number):
            return Number(self.value ** other.value).set_context(self.context), None
        else:
            return None, self.illegal_operation(self, other)
        
    def modulo_by(self, other):
        """A function to represent modulo operations."""
        if isinstance(other, Number):
            if other.value == 0:
                return None, EjecucionError(
                    other.pos_start, other.pos_end, 'Division por zero',
                    self.context
                )
            return Number(self.value % other.value).set_context(self.context), None
        else:
            return None, self.illegal_operation(self, other)
        
    def floordiv_by(self, other):
        """A function to represent floor division."""
        if isinstance(other, Number):
            if other.value == 0:
                return None, EjecucionError(
                    other.pos_start, other.pos_end, 'Division por zero', self.context
                )
            return Number(self.value // other.value).set_context(self.context), None
        else:
            return None, self.illegal_operation(self, other)
    
    def get_comparison_eq(self, other):
        """Handles equals comparisons."""
        if isinstance(other, Number):
            return Number(int(self.value == other.value)).set_context(self.context), None
        else:
            return None, self.illegal_operation(self, other)
        
    def get_comparison_ne(self, other):
            """Handles inequality operations."""
            if isinstance(other, Number):
                return Number(int(self.value != other.value)).set_context(self.context), None
            else:
                return None, self.illegal_operation(self, other)

    def get_comparison_lt(self, other):
        """Less than comparisons."""
        if isinstance(other, Number):
            return Number(int(self.value < other.value)).set_context(self.context), None
        else:
            return None, self.illegal_operation(self, other)

    def get_comparison_lte(self, other):
        """Less than or equal to comparisons."""
        if isinstance(other, Number):
            return Number(int(self.value <= other.value)).set_context(self.context), None
        else:
            return None, self.illegal_operation(self, other)

    def get_comparison_gt(self, other):
        """Greater than comparisons."""
        if isinstance(other, Number):
            return Number(int(self.value > other.value)).set_context(self.context), None
        else:
            return None, self.illegal_operation(self, other)

    def get_comparison_gte(self, other):
        """Greater than or equal to comparisons."""
        if isinstance(other, Number):
            return Number(int(self.value >= other.value)).set_context(self.context), None
        else:
            return None, self.illegal_operation(self, other)

    def anded_by(self, other):
        if isinstance(other, Number):
            return Number(int(self.value and other.value)).set_context(self.context), None
        else:
            return None, self.illegal_operation(self, other)

    def ored_by(self, other):
        if isinstance(other, Number):
            return Number(int(self.value or other.value)).set_context(self.context), None
        else:
            return None, self.illegal_operation(self, other)
        
    def notted(self):
        return Number(1 if self.value == 0 else 0).set_context(self.context), None
    
    def is_true(self):
        return self.value != 0

    def copy(self):
        """A function to copy an operations position."""
        copy = Number(self.value)
        copy.set_position(self.pos_start, self.pos_end)
        copy.set_context(self.context)
        return copy
        
    def __repr__(self):
        return str(self.value)
    
class String(Value):
    def __init__(self, value):
        super().__init__()
        self.value = value

    def added_to(self, other):
        if isinstance(other, String):
            return String(self.value + other.value).set_context(self.context), None
        return None, self.illegal_operation(self, other)
    
    def multed_by(self, other):
        if isinstance(other, Number):
            return String(self.value * other.value).set_context(self.context), None
        return None, self.illegal_operation(self, other)
    
    def is_true(self):
        return len(self.value) > 0
    
    def copy(self):
        copy = String(self.value)
        copy.set_position(self.pos_start, self.pos_end)
        copy.set_context(self.context)
        return copy
    
    def __repr__(self):
        return f"{self.value}"
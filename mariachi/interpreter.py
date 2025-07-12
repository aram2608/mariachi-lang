import os

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
        value = value.copy().set_position(node.pos_start, node.pos_end).set_context(context)
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

    def visit_BlockNode(self, node, context):
        res = RTResult()
        result = None

        for statement in node.statements:
            result = res.register(self.visit(statement, context))
            if res.error: return res

        # Return last statement's result
        return res.success(result or None)
    
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
    
    def visit_ForNode(self, node, context):
        res = RTResult()
        elements = []

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

            elements.append(res.register(self.visit(node.body_node, context)))
            if res.error: return res
        return res.success(List(elements).with_meta(context, pos_start=node.pos_start, pos_end=node.pos_end))

    def visit_WhileNode(self, node, context):
        res = RTResult()
        elements = []
        while True:
            condition = res.register(self.visit(node.condition_node, context))
            if res.error: return res

            if not condition.is_true(): break

            elements.append(res.register(self.visit(node.body_node, context)))
            if res.error: return res
        return res.success(List(elements).with_meta(context, pos_start=node.pos_start, pos_end=node.pos_end))
    
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
        return_value = return_value.copy().with_meta(context, node.pos_start, node.pos_end)
        return res.success(return_value)
    
    def visit_StringNode(self, node, context):
        return RTResult().success(
            String(node.tok.value).with_meta(context, node.pos_start, node.pos_end))
    
    def visit_ListNode(self, node, context):
        res = RTResult()
        elements = []

        for element_node in node.element_nodes:
            elements.append(res.register(self.visit(element_node, context)))
            if res.error: return res

        return res.success(
            List(elements).with_meta(context, node.pos_start, node.pos_end))

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
    
class BaseFunction(Value):
    def __init__(self, name):
        super().__init__()
        self.name = name or "<anonimo>"

    def generate_new_context(self):
        new_context = Context(self.name, self.context, self.pos_start)
        new_context.symbol_table = SymbolTable(new_context.parent.symbol_table)
        return new_context
    
    def check_args(self, arg_names, args):
        res = RTResult()

        if len(args) > len(arg_names):
            return res.failure(EjecucionError(
                self.pos_start, self.pos_end,
                f"{len(args) - len(arg_names)} demasiados argumentos pasados a '{self.name}'",
                self.context
            ))

        if len(args) < len(arg_names):
            return res.failure(EjecucionError(
                self.pos_start, self.pos_end,
                f"{len(arg_names) - len(args)} no suficiente argumentos pasados a '{self.name}'",
                self.context
            ))
        return res.success(None)
    
    def populate_args(self, arg_names, args, exec_ctx):
        for i in range(len(args)):
            arg_name = arg_names[i]
            arg_value = args[i]
            arg_value.set_context(exec_ctx)
            exec_ctx.symbol_table.set(arg_name, arg_value)

    def check_and_populate_args(self, arg_names, args, exec_ctx):
        res = RTResult()
        res.register(self.check_args(arg_names, args))
        if res.error: return res
        self.populate_args(arg_names, args, exec_ctx)
        return res.success(None)

class Function(BaseFunction):
    def __init__(self, name, body_node, arg_names):
        super().__init__(name)
        self.body_node = body_node
        self.arg_names = arg_names

    def execute(self, args):
        res = RTResult()
        interpreter = Interpreter()
        exec_ctx = self.generate_new_context()
        
        res.register(self.check_and_populate_args(self.arg_names, args, exec_ctx))
        if res.error:
            return res

        value = res.register(interpreter.visit(self.body_node, exec_ctx))
        if res.error:
            return
        return res.success(value)

    def copy(self):
        copy = Function(self.name, self.body_node, self.arg_names)
        copy.set_context(self.context)
        copy.set_position(self.pos_start, self.pos_end)
        return copy

    def __repr__(self):
        return f"<funcion {self.name}>"

class BuiltInFunction(BaseFunction):
    def __init__(self, name):
        super().__init__(name)

    def execute(self, args):
        res = RTResult()
        exec_ctx = self.generate_new_context()

        method_name = f'execute_{self.name}'
        method = getattr(self, method_name, self.no_visit_method)

        res.register(self.check_and_populate_args(method.arg_names, args, exec_ctx))
        if res.error: return

        return_value = res.register(method(exec_ctx))
        if res.error: return res
        return res.success(return_value)
    
    def no_visit_method(self, node, context):
        raise Exception(f"execute_{self.name} function not defined.")
        
    def copy(self):
        copy = BuiltInFunction(self.name)
        copy.set_context(self.context)
        copy.set_position(self.pos_start, self.pos_end)
        return copy

    def __repr__(self):
        return f"<built-in function {self.name}>"

    def execute_canta(self, exec_ctx):
        print(str(exec_ctx.symbol_table.get('value')))
        return RTResult().success(Number.null)
    execute_canta.arg_names = ['value']

    def execute_print_ret(self, exec_ctx):
        return RTResult().success(String(str(exec_ctx.symbol_table.get('value'))))
    execute_print_ret.arg_names = ['value']

    def execute_input(self, exec_ctx):
        text = input()
        return RTResult.success(String(text))
    execute_input.arg_names = []

    def execute_input_int(self, exec_ctx):
        while True:
            text = input()
            try:
                number = int(text)
                break
            except ValueError:
                print(f"{text} debe de ser un numero")
        return RTResult().success(Number(number))
    execute_input_int.arg_names = []

    def execute_clear(self, exec_ctx):
        os.system('cls' if os.name == 'nt' else 'clear')
        return RTResult().success(Number.null)
    execute_clear.arg_names = []

    def execute_is_number(self, exec_ctx):
        is_number = isinstance(exec_ctx.symbol_table.get("value"), Number)
        return RTResult().success(Number.true if is_number else Number.false)
    execute_is_number.arg_names = ["value"]

    def execute_is_string(self, exec_ctx):
        is_string = isinstance(exec_ctx.symbol_table.get("value"), String)
        return RTResult().success(Number.true if is_string else Number.false)
    execute_is_string.arg_names = ["value"]

    def execute_is_list(self, exec_ctx):
        is_list = isinstance(exec_ctx.symbol_table.get("value"), List)
        return RTResult().success(Number.true if is_list else Number.false)
    execute_is_list.arg_names = ["value"]

    def execute_is_function(self, exec_ctx):
        is_function = isinstance(exec_ctx.symbol_table.get("value"), BaseFunction)
        return RTResult().success(Number.true if is_function else Number.false)
    execute_is_function.arg_names = ["value"]

    def execute_append(self, exec_ctx):
        list_ = exec_ctx.symbol_table.get("list")
        value = exec_ctx.symbol_table.get("value")

        if not isinstance(list_, List):
            return RTResult().failure(EjecucionError(
                self.pos_start, self.pos_end,
                "First argument must be list",
                exec_ctx
            ))

        list_.elements.append(value)
        return RTResult().success(Number.null)
    execute_append.arg_names = ["list", "value"]

    def execute_pop(self, exec_ctx):
        list_ = exec_ctx.symbol_table.get("list")
        index = exec_ctx.symbol_table.get("index")

        if not isinstance(list_, List):
            return RTResult().failure(EjecucionError(
                self.pos_start, self.pos_end,
                "First argument must be list",
                exec_ctx
            ))

        if not isinstance(index, Number):
            return RTResult().failure(EjecucionError(
                self.pos_start, self.pos_end,
                "Second argument must be number",
                exec_ctx
            ))

        try:
            element = list_.elements.pop(index.value)
        except:
            return RTResult().failure(EjecucionError(
                self.pos_start, self.pos_end,
                'Element at this index could not be removed from list because index is out of bounds',
                exec_ctx
            ))

        return RTResult().success(element)
    execute_pop.arg_names = ["list", "index"]

    def execute_extend(self, exec_ctx):
        listA = exec_ctx.symbol_table.get("listA")
        listB = exec_ctx.symbol_table.get("listB")

        if not isinstance(listA, List):
            return RTResult().failure(EjecucionError(
                self.pos_start, self.pos_end,
                "First argument must be list",
                exec_ctx
            ))

        if not isinstance(listB, List):
            return RTResult().failure(EjecucionError(
                self.pos_start, self.pos_end,
                "Second argument must be list",
                exec_ctx
            ))

        listA.elements.extend(listB.elements)
        return RTResult().success(Number.null)
    execute_extend.arg_names = ["listA", "listB"]

BuiltInFunction.canta       = BuiltInFunction("canta")
BuiltInFunction.eco         = BuiltInFunction("eco")
BuiltInFunction.escucha     = BuiltInFunction("escucha")
BuiltInFunction.escucha_num = BuiltInFunction("escucha_num")
BuiltInFunction.limpia      = BuiltInFunction("limpia")
BuiltInFunction.es_num      = BuiltInFunction("es_num")
BuiltInFunction.es_texto    = BuiltInFunction("es_texto")
BuiltInFunction.es_lista    = BuiltInFunction("es_lista")
BuiltInFunction.es_funcion  = BuiltInFunction("es_funcion")
BuiltInFunction.añade       = BuiltInFunction("añade")
BuiltInFunction.quita       = BuiltInFunction("quita")
BuiltInFunction.extiende    = BuiltInFunction("extiende")

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
    
Number.null = Number(0)
Number.true = Number(1)
Number.false = Number(0)
    
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
    
class List(Value):
    def __init__(self, elements):
        super().__init__()
        self.elements = elements

    def added_to(self, other):
        new_list = self.copy()
        new_list.elements.append(other)
        return new_list, None
    
    def multed_by(self, other):
        if isinstance(other, List):
            new_list = self.copy()
            new_list.elements.extend(other.elements)
            return new_list, None
        else:
            return None, self.illegal_operation(self, other)
        
    def subbed_by(self, other):
        if isinstance(other, Number):
            new_list = self.copy()
            try:
                new_list.elements.pop(other.value)
                return new_list, None
            except:
                return None, EjecucionError(
                    other.pos_start, other.pos_end, 'El indice esta afuera de la lista', self.context)
        else:
            return None, self.illegal_operation(self, other)
        
    def divided_by(self, other):
        if isinstance(other, Number):
            try:
                return self.elements[other.value], None
            except:
                return None, EjecucionError(
                    other.pos_start, other.pos_end, 'El indice esta afuera de la lista', self.context)
        else:
            return None, self.illegal_operation(self, other)
        
    def copy(self):
        copy = List(self.elements)
        copy.set_position(self.pos_start, self.pos_end)
        copy.set_context(self.context)
        return copy
    
    def __repr__(self):
        return f'[{", ".join([str(x) for x in self.elements])}]'
from .lexer import *
from .nodes import *
from .token import *
from .interpreter import *
from .context import *


class Parser:
    """The parser class for our language."""

    def __init__(self, tokens):
        self.tokens = tokens
        self.tok_idx = -1
        self.repl = False
        self.advance()

    def advance(self):
        """Advance through our tokens."""
        self.tok_idx += 1
        self.update_current_tok()
        return self.current_tok

    def reverse(self, amount=1):
        self.tok_idx -= amount
        self.update_current_tok()
        return self.current_tok

    def update_current_tok(self):
        if self.tok_idx >= 0 and self.tok_idx < len(self.tokens):
            self.current_tok = self.tokens[self.tok_idx]

    def parse(self):
        """Parser function for the grammar rules."""
        res = self.statements()
        if not res.error and self.current_tok.type != TT_EOF:
            return res.failure(
                SintaxisInvalidoError(
                    self.current_tok.pos_start,
                    self.current_tok.pos_end,
                    "'+', '-', '*', '/', '^', '==', '!=', '<', '>', <=', '>=', 'y' or 'o' esperado",
                )
            )
        return res

    ####################################

    def block(self):
        res = ParseResult()

        if self.current_tok.type != TT_LBRACE:
            return res.failure(
                SintaxisInvalidoError(
                    self.current_tok.pos_start, self.current_tok.pos_end, "'{' esperado"
                )
            )

        res.register_advancement()
        self.advance()

        statements = res.register(self.statements())
        if res.error:
            return res

        if self.current_tok.type != TT_RBRACE:
            return res.failure(
                SintaxisInvalidoError(
                    self.current_tok.pos_start, self.current_tok.pos_end, "'}' esperado"
                )
            )

        res.register_advancement()
        self.advance()

        return res.success(statements)

    def statements(self):
        res = ParseResult()
        statements = []
        pos_start = self.current_tok.pos_start.copy()

        while self.current_tok.type == TT_NEWLINE:
            res.register_advancement()
            self.advance()

        stmt = res.register(self.expr())
        if res.error:
            return res
        statements.append(stmt)
        more_stmts = True

        while True:
            nl_count = 0
            while self.current_tok.type == TT_NEWLINE:
                res.register_advancement()
                self.advance()
                nl_count += 1

            if nl_count == 0:
                more_stmts = False

            if not more_stmts:
                break

            stmt = res.try_register(self.expr())
            if not stmt:
                self.reverse(res.to_reverse_count)
                more_stmts = False
                continue
            statements.append(stmt)
        return res.success(
            ListNode(statements, pos_start, self.current_tok.pos_end.copy())
        )

    def expr(self):
        """Creates our expression."""
        res = ParseResult()

        # Assigning constants
        if self.current_tok.matches(TT_KEYWORD, "fija"):
            res.register_advancement()
            self.advance()

            if self.current_tok.type != TT_IDENTIFIER:
                return res.failure(
                    SintaxisInvalidoError(
                        self.current_tok.pos_start,
                        self.current_tok.pos_end,
                        "Identificador esperado",
                    )
                )

            const_name = self.current_tok
            res.register_advancement()
            self.advance()

            if self.current_tok.type != TT_EQ:
                return res.failure(
                    SintaxisInvalidoError(
                        self.current_tok.pos_start,
                        self.current_tok.pos_end,
                        "'=' esperado",
                    )
                )

            res.register_advancement()
            self.advance()

            value = res.register(self.expr())
            if res.error:
                return res
            return res.success(ConstAssignNode(const_name, value))

        # Assigning variables
        if self.current_tok.matches(TT_KEYWORD, "sea"):
            res.register_advancement()
            self.advance()

            # Check to make sure following token is an indentifier
            if self.current_tok.type != TT_IDENTIFIER:
                return res.failure(
                    SintaxisInvalidoError(
                        self.current_tok.pos_start,
                        self.current_tok.pos_end,
                        "Identificador esperado",
                    )
                )

            # Assigns the variable name
            var_name = self.current_tok
            res.register_advancement()
            self.advance()

            # Check to ensure that following a var name is an =
            if self.current_tok.type != TT_EQ:
                return res.failure(
                    SintaxisInvalidoError(
                        self.current_tok.pos_start,
                        self.current_tok.pos_end,
                        "'=' esperado",
                    )
                )

            # Assign a new expression to the created variable
            res.register_advancement()
            self.advance()
            expr = res.register(self.expr())
            if res.error:
                return res
            return res.success(VarAssignNode(var_name, expr))

        node = res.register(
            self.binary_operation(
                self.comp_expr, ((TT_KEYWORD, "y"), (TT_KEYWORD, "o"))
            )
        )

        if res.error:
            return res.failure(
                SintaxisInvalidoError(
                    self.current_tok.pos_start,
                    self.current_tok.pos_end,
                    "'sea', int, float, identificador, '+', '-', '(', '[', o 'jamas' esperado",
                )
            )
        return res.success(node)

    def comp_expr(self):
        """Handles comparison expression."""
        res = ParseResult()

        if self.current_tok.matches(TT_KEYWORD, "jamas"):
            op_tok = self.current_tok
            res.register_advancement()
            self.advance()

            node = res.register(self.comp_expr())
            if res.error:
                return res
            return res.success(UnaryOpNode(op_tok, node))

        node = res.register(
            self.binary_operation(
                self.arith_expr, (TT_EE, TT_NE, TT_LT, TT_LTE, TT_GT, TT_GTE)
            )
        )
        if res.error:
            return res.failure(
                SintaxisInvalidoError(
                    self.current_tok.pos_start,
                    self.current_tok.pos_end,
                    "'+', '-', '(', '[', 'si', 'para', 'mientras', 'define' o 'jamas' esperado",
                )
            )
        return res.success(node)

    def arith_expr(self):
        """Handles arithmetic logic."""
        return self.binary_operation(self.term, (TT_PLUS, TT_MINUS))

    def term(self):
        """Creates our terms."""
        return self.binary_operation(self.factor, (TT_DIV, TT_MUL, TT_MOD, TT_FLOORDIV))

    def factor(self):
        """Logic for handling factors."""
        res = ParseResult()
        tok = self.current_tok
        # Checks to see if our token type is a plus or a minus
        if tok.type in (TT_PLUS, TT_MINUS):
            res.register_advancement()
            self.advance()
            factor = res.register(self.factor())
            # Check for any errors
            if res.error:
                return res
            return res.success(UnaryOpNode(tok, factor))
        return self.power()

    def power(self):
        """Handles powers."""
        return self.binary_operation(self.call, (TT_POW,), self.factor)

    def call(self):
        res = ParseResult()
        atom = res.register(self.atom())
        if res.error:
            return res

        if self.current_tok.type == TT_LPAREN:
            res.register_advancement()
            self.advance()
            arg_nodes = []

            if self.current_tok.type == TT_RPAREN:
                res.register_advancement()
                self.advance()
            else:
                arg_nodes.append(res.register(self.expr()))
                if res.error:
                    return res.failure(
                        SintaxisInvalidoError(
                            self.current_tok.pos_start,
                            self.current_tok.pos_end,
                            "')', 'sea', 'si', 'para', 'mientras', int, float, identificador, '+', '-', '(', '[' o 'jamas' esperado",
                        )
                    )

                while self.current_tok.type == TT_COMMA:
                    res.register_advancement()
                    self.advance()

                    arg_nodes.append(res.register(self.expr()))
                    if res.error:
                        return res

                if self.current_tok.type != TT_RPAREN:
                    return res.failure(
                        SintaxisInvalidoError(
                            self.current_tok.pos_start,
                            self.current_tok.pos_end,
                            "',' o ')' esperado",
                        )
                    )

                res.register_advancement()
                self.advance()
            return res.success(CallNode(atom, arg_nodes))
        return res.success(atom)

    def atom(self):
        """Logic for handling atoms."""
        res = ParseResult()
        tok = self.current_tok

        # Checks if our current token is a number type
        if tok.type in (TT_INT, TT_FLOAT):
            res.register_advancement()
            self.advance()
            return res.success(NumberNode(tok))

        # Handling strings
        elif tok.type == (TT_STRING):
            res.register_advancement()
            self.advance()
            return res.success(StringNode(tok))

        # Check for identifier
        elif tok.type == TT_IDENTIFIER:
            res.register_advancement()
            self.advance()
            return res.success(VarAccessNode(tok))

        # Check for brackets
        elif tok.type == TT_LSQUARE:
            list_expr = res.register(self.list_expr())
            if res.error:
                return res
            return res.success(list_expr)

        # Parenthesis check
        elif tok.type == TT_LPAREN:
            res.register_advancement()
            self.advance()
            expr = res.register(self.expr())
            # Check for errors
            if res.error:
                return res
            if self.current_tok.type == TT_RPAREN:
                res.register_advancement()
                self.advance()
                return res.success(expr)
            else:
                return res.failure(
                    SintaxisInvalidoError(
                        self.current_tok.pos_start,
                        self.current_tok.pos_end,
                        "')' esperado",
                    )
                )
        # If statement
        elif tok.matches(TT_KEYWORD, "si"):
            if_expr = res.register(self.if_expr())
            if res.error:
                return res
            return res.success(if_expr)

        # For statement
        elif tok.matches(TT_KEYWORD, "para"):
            for_expr = res.register(self.for_expr())
            if res.error:
                return res
            return res.success(for_expr)

        # While expression
        elif tok.matches(TT_KEYWORD, "mientras"):
            while_expr = res.register(self.while_expr())
            if res.error:
                return res
            return res.success(while_expr)

        # Define functions
        elif tok.matches(TT_KEYWORD, "define"):
            func_expr = res.register(self.func_def())
            if res.error:
                return res
            return res.success(func_expr)

        return res.failure(
            SintaxisInvalidoError(
                tok.pos_start,
                tok.pos_end,
                "int, float, identificador, '+', '-', '(', '[', 'si', 'para', 'mientras', o 'define' esperado",
            )
        )

    def list_expr(self):
        res = ParseResult()
        element_nodes = []
        pos_start = self.current_tok.pos_start.copy()

        if self.current_tok.type != TT_LSQUARE:
            return res.failure(
                SintaxisInvalidoError(
                    self.current_tok.pos_start,
                    self.current_tok.pos_end,
                    f"'[' esperado",
                )
            )

        res.register_advancement()
        self.advance()

        if self.current_tok.type == TT_RSQUARE:
            res.register_advancement()
            self.advance()
        else:
            element_nodes.append(res.register(self.expr()))
            if res.error:
                return res.failure(
                    SintaxisInvalidoError(
                        self.current_tok.pos_start,
                        self.current_tok.pos_end,
                        "']', 'sea', 'define', 'para', 'mientras', int, float, identificador, '+', '-', '(', '[' o 'jamas' esperado",
                    )
                )

            while self.current_tok.type == TT_COMMA:
                res.register_advancement()
                self.advance()

                element_nodes.append(res.register(self.expr()))
                if res.error:
                    return res

            if self.current_tok.type != TT_RSQUARE:
                return res.failure(
                    SintaxisInvalidoError(
                        self.current_tok.pos_start,
                        self.current_tok.pos_end,
                        "',' o ')' esperado",
                    )
                )

            res.register_advancement()
            self.advance()
        return res.success(
            ListNode(element_nodes, pos_start, self.current_tok.pos_end.copy())
        )

    def if_expr(self):
        res = ParseResult()
        cases = []
        else_case = None

        if not self.current_tok.matches(TT_KEYWORD, "si"):
            return res.failure(
                SintaxisInvalidoError(
                    self.current_tok.pos_start,
                    self.current_tok.pos_end,
                    "'si' esperado",
                )
            )

        res.register_advancement()
        self.advance()

        condition = res.register(self.expr())
        if res.error:
            return res

        body = res.register(self.block())
        if res.error:
            return res

        cases.append((condition, body))

        while self.current_tok.matches(TT_KEYWORD, "quizas"):
            res.register_advancement()
            self.advance()

            condition = res.register(self.expr())
            if res.error:
                return res

            body = res.register(self.block())
            if res.error:
                return res

            cases.append((condition, body))

        if self.current_tok.matches(TT_KEYWORD, "sino"):
            res.register_advancement()
            self.advance()

            body = res.register(self.block())
            if res.error:
                return res

            else_case = body

        return res.success(IfNode(cases, else_case))

    def for_expr(self):
        res = ParseResult()

        if not self.current_tok.matches(TT_KEYWORD, "para"):
            return res.failure(
                SintaxisInvalidoError(
                    self.current_tok.pos_start,
                    self.current_tok.pos_end,
                    "'para' esperado",
                )
            )

        res.register_advancement()
        self.advance()

        if self.current_tok.type != TT_IDENTIFIER:
            return res.failure(
                SintaxisInvalidoError(
                    self.current_tok.pos_start,
                    self.current_tok.pos_end,
                    "Identificador esperado",
                )
            )

        var_name = self.current_tok
        res.register_advancement()
        self.advance()

        if self.current_tok.type != TT_EQ:
            return res.failure(
                SintaxisInvalidoError(
                    self.current_tok.pos_start, self.current_tok.pos_end, "'=' esperado"
                )
            )

        res.register_advancement()
        self.advance()

        start_value = res.register(self.expr())
        if res.error:
            return res

        if not self.current_tok.matches(TT_KEYWORD, "hasta"):
            return res.failure(
                SintaxisInvalidoError(
                    self.current_tok.pos_start,
                    self.current_tok.pos_end,
                    "'hasta' esperado",
                )
            )

        res.register_advancement()
        self.advance()

        end_value = res.register(self.expr())
        if res.error:
            return res

        step_value = None
        if self.current_tok.matches(TT_KEYWORD, "paso"):
            res.register_advancement()
            self.advance()
            step_value = res.register(self.expr())
            if res.error:
                return res

        body = res.register(self.block())
        if res.error:
            return res

        return res.success(
            ForNode(var_name, start_value, end_value, step_value, body, True)
        )

    def while_expr(self):
        res = ParseResult()

        if not self.current_tok.matches(TT_KEYWORD, "mientras"):
            return res.failure(
                SintaxisInvalidoError(
                    self.current_tok.pos_start,
                    self.current_tok.pos_end,
                    "'mientras' esperado",
                )
            )

        res.register_advancement()
        self.advance()

        condition = res.register(self.expr())
        if res.error:
            return res

        body = res.register(self.block())
        if res.error:
            return res

        return res.success(WhileNode(condition, body, True))

    def func_def(self):
        """Defines functions."""
        res = ParseResult()

        if not self.current_tok.matches(TT_KEYWORD, "define"):
            return res.failure(
                SintaxisInvalidoError(
                    self.current_tok.pos_start,
                    self.current_tok.pos_end,
                    "'define' esperado",
                )
            )

        res.register_advancement()
        self.advance()

        if self.current_tok.type == TT_IDENTIFIER:
            var_name_tok = self.current_tok
            res.register_advancement()
            self.advance()

            if self.current_tok.type != TT_LPAREN:
                return res.failure(
                    SintaxisInvalidoError(
                        self.current_tok.pos_start,
                        self.current_tok.pos_end,
                        "'(' esperado",
                    )
                )
        else:
            var_name_tok = None
            if self.current_tok.type != TT_LPAREN:
                return res.failure(
                    SintaxisInvalidoError(
                        self.current_tok.pos_start,
                        self.current_tok.pos_end,
                        "'identificador o '(' esperado",
                    )
                )

        res.register_advancement()
        self.advance()

        arg_name_toks = []

        if self.current_tok.type == TT_IDENTIFIER:
            arg_name_toks.append(self.current_tok)
            res.register_advancement()
            self.advance()

            while self.current_tok.type == TT_COMMA:
                res.register_advancement()
                self.advance()

                if self.current_tok.type != TT_IDENTIFIER:
                    return res.failure(
                        SintaxisInvalidoError(
                            self.current_tok.pos_start,
                            self.current_tok.pos_end,
                            "identificador esperado",
                        )
                    )

                arg_name_toks.append(self.current_tok)
                res.register_advancement()
                self.advance()

            if self.current_tok.type != TT_RPAREN:
                return res.failure(
                    SintaxisInvalidoError(
                        self.current_tok.pos_start,
                        self.current_tok.pos_end,
                        "')' esperado",
                    )
                )
        else:
            if self.current_tok.type != TT_RPAREN:
                return res.failure(
                    SintaxisInvalidoError(
                        self.current_tok.pos_start,
                        self.current_tok.pos_end,
                        "'identificador o '(' esperado",
                    )
                )

        res.register_advancement()
        self.advance()

        body = res.register(self.block())
        if res.error:
            return res

        res.register_advancement()
        self.advance()

        return res.success(FuncDefNode(var_name_tok, arg_name_toks, body, True))

    def binary_operation(self, func_a, ops, func_b=None):
        """Refactored logic for handling operators."""
        if func_b == None:
            func_b = func_a

        res = ParseResult()
        left = res.register(func_a())
        # Early exit if an error is found
        if res.error:
            return res

        while (
            self.current_tok.type in ops
            or (self.current_tok.type, self.current_tok.value) in ops
        ):
            # We assign the operation tokens
            op_tok = self.current_tok

            # We have to advance to prevent infinite loops

            res.register_advancement()
            self.advance()

            # We assign the right factor
            right = res.register(func_b())

            # Early exit if an error is found
            if res.error:
                return res

            # Reassign to a BindaryOpNode
            left = BinaryOpNode(left, op_tok, right)
        return res.success(left)

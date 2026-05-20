from src.ast_nodes import *


class ReturnSignal(Exception):
    def __init__(self, value):
        self.value = value


class Environment:
    def __init__(self, parent=None):
        self.variables = {}
        self.parent = parent

    def define(self, name, value):
        self.variables[name] = value

    def get(self, name):
        if name in self.variables:
            return self.variables[name]
        if self.parent:
            return self.parent.get(name)
        raise RuntimeError(f"Undefined variable: '{name}'")

    def set(self, name, value):
        if name in self.variables:
            self.variables[name] = value
            return
        if self.parent:
            self.parent.set(name, value)
            return
        raise RuntimeError(f"Undefined variable: '{name}'")


class Interpreter:
    """
    Tree-walking interpreter - executes the AST directly
    """

    def __init__(self):
        self.global_env = Environment()
        self.current_env = self.global_env
        self.functions = {} 
        self.output_lines = [] 

    def interpret(self, ast):
        """Execute the AST and return collected output"""
        if ast is None:
            return self.output_lines
        self._visit(ast)
        return self.output_lines

    def _visit(self, node):
        method_name = f'_visit_{type(node).__name__}'
        visitor = getattr(self, method_name, self._generic_visit)
        return visitor(node)

    def _generic_visit(self, node):
        pass

    def _visit_ProgramNode(self, node):
        for stmt in node.statements:
            self._visit(stmt)

    def _visit_DeclarationNode(self, node):
        value = self._visit(node.value)
        self.current_env.define(node.name, value)

    def _visit_AssignmentNode(self, node):
        value = self._visit(node.value)
        self.current_env.set(node.name, value)

    def _visit_PrintNode(self, node):
        value = self._visit(node.expression)
        self.output_lines.append(str(value))

    def _visit_IfNode(self, node):
        condition = self._visit(node.condition)
        if condition:
            self._visit(node.if_body)
        elif node.else_body:
            self._visit(node.else_body)

    def _visit_WhileNode(self, node):
        while self._visit(node.condition):
            self._visit(node.body)

    def _visit_BlockNode(self, node):
        for stmt in node.statements:
            self._visit(stmt)

    def _visit_FunctionDeclNode(self, node):
        self.functions[node.name] = node

    def _visit_ReturnNode(self, node):
        value = self._visit(node.expression)
        raise ReturnSignal(value)

    def _visit_BinaryOpNode(self, node):
        left = self._visit(node.left)
        right = self._visit(node.right)

        if node.op == '+':
            return left + right
        elif node.op == '-':
            return left - right
        elif node.op == '*':
            return left * right
        elif node.op == '/':
            if right == 0:
                raise RuntimeError("Division by zero")
            if isinstance(left, int) and isinstance(right, int):
                return left // right
            return left / right
        elif node.op == '%':
            if right == 0:
                raise RuntimeError("Modulo by zero")
            return left % right
        elif node.op == '==':
            return left == right
        elif node.op == '!=':
            return left != right
        elif node.op == '<':
            return left < right
        elif node.op == '>':
            return left > right
        elif node.op == '<=':
            return left <= right
        elif node.op == '>=':
            return left >= right
        elif node.op == 'wa':  # AND
            return int(left and right)
        elif node.op == 'aw':  # OR
            return left or right

        return None

    def _visit_UnaryOpNode(self, node):
        operand = self._visit(node.operand)
        if node.op == '-':
            return -operand
        elif node.op == 'lays':  # NOT
            return not operand
        return None

    def _visit_NumberNode(self, node):
        return node.value

    def _visit_FloatNode(self, node):
        return node.value

    def _visit_StringNode(self, node):
        return node.value

    def _visit_BoolNode(self, node):
        return node.value

    def _visit_IdentifierNode(self, node):
        return self.current_env.get(node.name)

    def _visit_FunctionCallNode(self, node):
        func = self.functions.get(node.name)
        if func is None:
            raise RuntimeError(f"Undefined function: '{node.name}'")

        args = [self._visit(arg) for arg in node.args]

        func_env = Environment(parent=self.global_env)
        for (param_name, _), arg_val in zip(func.params, args):
            func_env.define(param_name, arg_val)

        old_env = self.current_env
        self.current_env = func_env
        try:
            self._visit(func.body)
        except ReturnSignal as ret:
            self.current_env = old_env
            return ret.value
        self.current_env = old_env
        return None

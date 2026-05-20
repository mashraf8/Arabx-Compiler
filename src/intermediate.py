from src.ast_nodes import *


class TACInstruction:
    def __init__(self, op, arg1=None, arg2=None, result=None):
        self.op = op
        self.arg1 = arg1
        self.arg2 = arg2
        self.result = result

    def __str__(self):
        if self.op == 'LABEL':
            return f"{self.result}:"
        elif self.op == 'GOTO':
            return f"  GOTO {self.result}"
        elif self.op == 'IF_TRUE':
            return f"  IF {self.arg1} GOTO {self.result}"
        elif self.op == 'IF_FALSE':
            return f"  IF_FALSE {self.arg1} GOTO {self.result}"
        elif self.op == 'ASSIGN':
            return f"  {self.result} = {self.arg1}"
        elif self.op == 'PRINT':
            return f"  PRINT {self.arg1}"
        elif self.op == 'RETURN':
            return f"  RETURN {self.arg1}"
        elif self.op == 'PARAM':
            return f"  PARAM {self.arg1}"
        elif self.op == 'CALL':
            return f"  {self.result} = CALL {self.arg1}, {self.arg2}"
        elif self.op == 'FUNC_BEGIN':
            return f"  FUNC_BEGIN {self.arg1}"
        elif self.op == 'FUNC_END':
            return f"  FUNC_END {self.arg1}"
        elif self.op in ('+', '-', '*', '/', '%', '==', '!=', '<', '>', '<=', '>=', 'wa', 'aw'):
            return f"  {self.result} = {self.arg1} {self.op} {self.arg2}"
        elif self.op == 'UMINUS':
            return f"  {self.result} = -{self.arg1}"
        elif self.op == 'NOT':
            return f"  {self.result} = NOT {self.arg1}"
        else:
            return f"  {self.op} {self.arg1} {self.arg2} {self.result}"


class IntermediateCodeGenerator:
    def __init__(self):
        self.instructions = []
        self.temp_count = 0
        self.label_count = 0

    def new_temp(self):
        name = f"t{self.temp_count}"
        self.temp_count += 1
        return name

    def new_label(self):
        name = f"L{self.label_count}"
        self.label_count += 1
        return name

    def emit(self, op, arg1=None, arg2=None, result=None):
        instr = TACInstruction(op, arg1, arg2, result)
        self.instructions.append(instr)
        return instr

    def generate(self, ast):
        if ast is None:
            return self.instructions
        self._visit(ast)
        return self.instructions

    def _visit(self, node):
        method_name = f'_visit_{type(node).__name__}'
        visitor = getattr(self, method_name, self._generic_visit)
        return visitor(node)

    def _generic_visit(self, node):
        return None

    def _visit_ProgramNode(self, node):
        for stmt in node.statements:
            self._visit(stmt)

    def _visit_DeclarationNode(self, node):
        value = self._visit(node.value)
        self.emit('ASSIGN', value, result=node.name)

    def _visit_AssignmentNode(self, node):
        value = self._visit(node.value)
        self.emit('ASSIGN', value, result=node.name)

    def _visit_PrintNode(self, node):
        value = self._visit(node.expression)
        self.emit('PRINT', value)

    def _visit_IfNode(self, node):
        cond = self._visit(node.condition)

        if node.else_body:
            else_label = self.new_label()
            end_label = self.new_label()

            self.emit('IF_FALSE', cond, result=else_label)
            self._visit(node.if_body)
            self.emit('GOTO', result=end_label)
            self.emit('LABEL', result=else_label)
            self._visit(node.else_body)
            self.emit('LABEL', result=end_label)
        else:
            end_label = self.new_label()
            self.emit('IF_FALSE', cond, result=end_label)
            self._visit(node.if_body)
            self.emit('LABEL', result=end_label)

    def _visit_WhileNode(self, node):
        start_label = self.new_label()
        end_label = self.new_label()

        self.emit('LABEL', result=start_label)
        cond = self._visit(node.condition)
        self.emit('IF_FALSE', cond, result=end_label)
        self._visit(node.body)
        self.emit('GOTO', result=start_label)
        self.emit('LABEL', result=end_label)

    def _visit_BlockNode(self, node):
        for stmt in node.statements:
            self._visit(stmt)

    def _visit_FunctionDeclNode(self, node):
        self.emit('FUNC_BEGIN', node.name)
        for param_name, _ in node.params:
            self.emit('PARAM', param_name)
        self._visit(node.body)
        self.emit('FUNC_END', node.name)

    def _visit_ReturnNode(self, node):
        value = self._visit(node.expression)
        self.emit('RETURN', value)

    def _visit_BinaryOpNode(self, node):
        left = self._visit(node.left)
        right = self._visit(node.right)
        temp = self.new_temp()
        self.emit(node.op, left, right, temp)
        return temp

    def _visit_UnaryOpNode(self, node):
        operand = self._visit(node.operand)
        temp = self.new_temp()
        if node.op == '-':
            self.emit('UMINUS', operand, result=temp)
        else:
            self.emit('NOT', operand, result=temp)
        return temp

    def _visit_NumberNode(self, node):
        return str(node.value)

    def _visit_FloatNode(self, node):
        return str(node.value)

    def _visit_StringNode(self, node):
        return f'"{node.value}"'

    def _visit_BoolNode(self, node):
        return '1' if node.value else '0'

    def _visit_IdentifierNode(self, node):
        return node.name

    def _visit_FunctionCallNode(self, node):
        args = []
        for arg in node.args:
            val = self._visit(arg)
            args.append(val)
        for a in args:
            self.emit('PARAM', a)
        temp = self.new_temp()
        self.emit('CALL', node.name, len(args), temp)
        return temp

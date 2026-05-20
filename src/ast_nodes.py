
class ASTNode:
    pass


class ProgramNode(ASTNode):
    def __init__(self, statements):
        self.statements = statements


class DeclarationNode(ASTNode):
    def __init__(self, name, var_type, value):
        self.name = name
        self.var_type = var_type
        self.value = value


class AssignmentNode(ASTNode):
    def __init__(self, name, value):
        self.name = name
        self.value = value


class PrintNode(ASTNode):
    def __init__(self, expression):
        self.expression = expression


class IfNode(ASTNode):
    def __init__(self, condition, if_body, else_body=None):
        self.condition = condition
        self.if_body = if_body
        self.else_body = else_body


class WhileNode(ASTNode):
    def __init__(self, condition, body):
        self.condition = condition
        self.body = body


class FunctionDeclNode(ASTNode):
    def __init__(self, name, params, return_type, body):
        self.name = name
        self.params = params
        self.return_type = return_type
        self.body = body


class ReturnNode(ASTNode):
    def __init__(self, expression):
        self.expression = expression


class BinaryOpNode(ASTNode):
    def __init__(self, op, left, right):
        self.op = op
        self.left = left
        self.right = right


class UnaryOpNode(ASTNode):
    def __init__(self, op, operand):
        self.op = op
        self.operand = operand


class NumberNode(ASTNode):
    def __init__(self, value):
        self.value = value


class FloatNode(ASTNode):
    def __init__(self, value):
        self.value = value


class StringNode(ASTNode):
    def __init__(self, value):
        self.value = value


class BoolNode(ASTNode):
    def __init__(self, value):
        self.value = value


class IdentifierNode(ASTNode):
    def __init__(self, name):
        self.name = name


class FunctionCallNode(ASTNode):
    def __init__(self, name, args):
        self.name = name
        self.args = args


class BlockNode(ASTNode):
    def __init__(self, statements):
        self.statements = statements

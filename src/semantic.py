from src.ast_nodes import *


class Symbol:
    def __init__(self, name, sym_type, kind='variable'):
        self.name = name
        self.sym_type = sym_type   
        self.kind = kind           


class SymbolTable:
    def __init__(self, parent=None):
        self.symbols = {}
        self.parent = parent

    def define(self, name, sym_type, kind='variable'):
        self.symbols[name] = Symbol(name, sym_type, kind)

    def lookup(self, name):
        if name in self.symbols:
            return self.symbols[name]
        if self.parent:
            return self.parent.lookup(name)
        return None

    def exists_local(self, name):
        return name in self.symbols

TYPE_MAP = {
    'sahih': 'sahih',
    'ashri': 'ashri',
    'nass': 'nass',
    'mantqi': 'mantqi',
}

NUMERIC_TYPES = {'sahih', 'ashri'}


class SemanticAnalyzer:

    def __init__(self):
        self.global_scope = SymbolTable()
        self.current_scope = self.global_scope
        self.errors = []
        self.warnings = []
        self.symbol_log = []  # Log of all symbols for display
        self.current_function_return_type = None

    def analyze(self, ast):
        if ast is None:
            self.errors.append("No AST to analyze (AST is None)")
            return False
        self._visit(ast)
        return len(self.errors) == 0

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
        if self.current_scope.exists_local(node.name):
            self.errors.append(f"Semantic Error: Variable '{node.name}' is already defined")
            return

        var_type = TYPE_MAP.get(node.var_type, node.var_type)
        value_type = self._visit(node.value)

        if value_type and var_type != value_type:
            if not (var_type in NUMERIC_TYPES and value_type in NUMERIC_TYPES):
                self.errors.append(
                    f"Semantic Error: Cannot assign value of type '{value_type}' to variable of type '{var_type}' (Variable: {node.name})"
                )

        self.current_scope.define(node.name, var_type)
        self.symbol_log.append({
            'name': node.name,
            'type': var_type,
            'kind': 'mutghyr',
            'scope': 'aam' if self.current_scope == self.global_scope else 'mahali'
        })
        return var_type

    def _visit_AssignmentNode(self, node):
        sym = self.current_scope.lookup(node.name)
        if sym is None:
            self.errors.append(f"Semantic Error: Variable '{node.name}' is undefined")
            return
        value_type = self._visit(node.value)
        if value_type and sym.sym_type != value_type:
            if not (sym.sym_type in NUMERIC_TYPES and value_type in NUMERIC_TYPES):
                self.errors.append(
                    f"Semantic Error: Cannot assign '{value_type}' to '{sym.sym_type}' (Variable: {node.name})"
                )

    def _visit_PrintNode(self, node):
        self._visit(node.expression)

    def _visit_IfNode(self, node):
        self._visit(node.condition)
        self._visit(node.if_body)
        if node.else_body:
            self._visit(node.else_body)

    def _visit_WhileNode(self, node):
        self._visit(node.condition)
        self._visit(node.body)

    def _visit_BlockNode(self, node):
        for stmt in node.statements:
            self._visit(stmt)

    def _visit_FunctionDeclNode(self, node):
        if self.current_scope.exists_local(node.name):
            self.errors.append(f"Semantic Error: Function '{node.name}' is already defined")
            return

        ret_type = TYPE_MAP.get(node.return_type, node.return_type)
        self.current_scope.define(node.name, ret_type, kind='function')
        self.symbol_log.append({
            'name': node.name,
            'type': ret_type,
            'kind': 'dalah',
            'scope': 'aam',
            'params': len(node.params)
        })

        func_scope = SymbolTable(parent=self.current_scope)
        old_scope = self.current_scope
        self.current_scope = func_scope

        old_ret = self.current_function_return_type
        self.current_function_return_type = ret_type

        for param_name, param_type in node.params:
            ptype = TYPE_MAP.get(param_type, param_type)
            func_scope.define(param_name, ptype)
            self.symbol_log.append({
                'name': param_name,
                'type': ptype,
                'kind': 'moaamel',
                'scope': f'dalah {node.name}'
            })

        self._visit(node.body)
        self.current_function_return_type = old_ret
        self.current_scope = old_scope

    def _visit_ReturnNode(self, node):
        ret_type = self._visit(node.expression)
        if self.current_function_return_type and ret_type:
            if self.current_function_return_type != ret_type:
                if not (self.current_function_return_type in NUMERIC_TYPES and ret_type in NUMERIC_TYPES):
                    self.errors.append(
                        f"Semantic Error: Return type '{ret_type}' does not match expected type '{self.current_function_return_type}'"
                    )
        return ret_type

    def _visit_BinaryOpNode(self, node):
        left_type = self._visit(node.left)
        right_type = self._visit(node.right)

        if node.op in ('+', '-', '*', '/', '%'):
            if left_type in NUMERIC_TYPES and right_type in NUMERIC_TYPES:
                if 'ashri' in (left_type, right_type):
                    return 'ashri'
                return 'sahih'
            if node.op == '+' and left_type == 'nass' and right_type == 'nass':
                return 'nass'
            if left_type and right_type:
                self.errors.append(
                    f"Semantic Error: Cannot apply operation '{node.op}' on '{left_type}' and '{right_type}'"
                )
            return left_type

        if node.op in ('==', '!=', '<', '>', '<=', '>='):
            return 'mantqi'

        if node.op in ('wa', 'aw'):
            return 'mantqi'

        return left_type

    def _visit_UnaryOpNode(self, node):
        operand_type = self._visit(node.operand)
        if node.op == '-' and operand_type not in NUMERIC_TYPES:
            self.errors.append(f"Semantic Error: Cannot apply negative sign to type '{operand_type}'")
        if node.op == 'lays' and operand_type != 'mantqi':
            self.errors.append(f"Semantic Error: 'NOT' requires a boolean value, not '{operand_type}'")
        if node.op == '-':
            return operand_type
        return 'mantqi'

    def _visit_NumberNode(self, node):
        return 'sahih'

    def _visit_FloatNode(self, node):
        return 'ashri'

    def _visit_StringNode(self, node):
        return 'nass'

    def _visit_BoolNode(self, node):
        return 'mantqi'

    def _visit_IdentifierNode(self, node):
        sym = self.current_scope.lookup(node.name)
        if sym is None:
            self.errors.append(f"Semantic Error: Variable '{node.name}' is undefined")
            return None
        return sym.sym_type

    def _visit_FunctionCallNode(self, node):
        sym = self.current_scope.lookup(node.name)
        if sym is None:
            self.errors.append(f"Semantic Error: Function '{node.name}' is undefined")
            return None
        if sym.kind != 'function':
            self.errors.append(f"Semantic Error: '{node.name}' is not a function")
            return None
        for arg in node.args:
            self._visit(arg)
        return sym.sym_type

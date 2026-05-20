import ply.yacc as yacc
from src.lexer import tokens, create_lexer
from src.ast_nodes import *

precedence = (
    ('left', 'AW'),
    ('left', 'WA'),
    ('nonassoc', 'EQ', 'NEQ'),
    ('nonassoc', 'LT', 'GT', 'LTE', 'GTE'),
    ('left', 'PLUS', 'MINUS'),
    ('left', 'TIMES', 'DIVIDE', 'MODULO'),
    ('right', 'LAYS'),
    ('right', 'UMINUS'),
)

def p_program(p):
    """program : statement_list"""
    p[0] = ProgramNode(p[1])


def p_statement_list_multi(p):
    """statement_list : statement_list statement"""
    p[0] = p[1] + [p[2]]


def p_statement_list_single(p):
    """statement_list : statement"""
    p[0] = [p[1]]


def p_statement(p):
    """statement : declaration
                 | assignment
                 | print_stmt
                 | if_stmt
                 | while_stmt
                 | function_decl
                 | return_stmt"""
    p[0] = p[1]

def p_declaration(p):
    """declaration : MUTGHYR IDENTIFIER COLON type ASSIGN expression SEMICOLON"""
    p[0] = DeclarationNode(p[2], p[4], p[6])


def p_type(p):
    """type : SAHIH
            | ASHRI
            | NASS
            | MANTQI"""
    p[0] = p[1]

def p_assignment(p):
    """assignment : IDENTIFIER ASSIGN expression SEMICOLON"""
    p[0] = AssignmentNode(p[1], p[3])

def p_print_stmt(p):
    """print_stmt : UTBAA LPAREN expression RPAREN SEMICOLON"""
    p[0] = PrintNode(p[3])

def p_if_else_stmt(p):
    """if_stmt : IDHA LPAREN expression RPAREN block WALA block"""
    p[0] = IfNode(p[3], p[5], p[7])


def p_if_stmt(p):
    """if_stmt : IDHA LPAREN expression RPAREN block"""
    p[0] = IfNode(p[3], p[5])

def p_while_stmt(p):
    """while_stmt : TALAMA LPAREN expression RPAREN block"""
    p[0] = WhileNode(p[3], p[5])

def p_function_decl(p):
    """function_decl : DALAH IDENTIFIER LPAREN param_list RPAREN COLON type block"""
    p[0] = FunctionDeclNode(p[2], p[4], p[7], p[8])


def p_function_decl_no_params(p):
    """function_decl : DALAH IDENTIFIER LPAREN RPAREN COLON type block"""
    p[0] = FunctionDeclNode(p[2], [], p[6], p[7])


def p_param_list_multi(p):
    """param_list : param_list COMMA param"""
    p[0] = p[1] + [p[3]]


def p_param_list_single(p):
    """param_list : param"""
    p[0] = [p[1]]


def p_param(p):
    """param : IDENTIFIER COLON type"""
    p[0] = (p[1], p[3])

def p_return_stmt(p):
    """return_stmt : IRJAA expression SEMICOLON"""
    p[0] = ReturnNode(p[2])

def p_block(p):
    """block : LBRACE statement_list RBRACE"""
    p[0] = BlockNode(p[2])

def p_expression_binop(p):
    """expression : expression PLUS expression
                  | expression MINUS expression
                  | expression TIMES expression
                  | expression DIVIDE expression
                  | expression MODULO expression
                  | expression EQ expression
                  | expression NEQ expression
                  | expression LT expression
                  | expression GT expression
                  | expression LTE expression
                  | expression GTE expression
                  | expression WA expression
                  | expression AW expression"""
    p[0] = BinaryOpNode(p[2], p[1], p[3])


def p_expression_uminus(p):
    """expression : MINUS expression %prec UMINUS"""
    p[0] = UnaryOpNode('-', p[2])


def p_expression_not(p):
    """expression : LAYS expression"""
    p[0] = UnaryOpNode('lays', p[2])


def p_expression_group(p):
    """expression : LPAREN expression RPAREN"""
    p[0] = p[2]


def p_expression_func_call(p):
    """expression : IDENTIFIER LPAREN arg_list RPAREN"""
    p[0] = FunctionCallNode(p[1], p[3])


def p_expression_func_call_no_args(p):
    """expression : IDENTIFIER LPAREN RPAREN"""
    p[0] = FunctionCallNode(p[1], [])


def p_arg_list_multi(p):
    """arg_list : arg_list COMMA expression"""
    p[0] = p[1] + [p[3]]


def p_arg_list_single(p):
    """arg_list : expression"""
    p[0] = [p[1]]


def p_expression_integer(p):
    """expression : INTEGER"""
    p[0] = NumberNode(p[1])


def p_expression_float(p):
    """expression : FLOAT_NUM"""
    p[0] = FloatNode(p[1])


def p_expression_string(p):
    """expression : STRING"""
    p[0] = StringNode(p[1])


def p_expression_true(p):
    """expression : TRUE"""
    p[0] = BoolNode(True)


def p_expression_false(p):
    """expression : FALSE"""
    p[0] = BoolNode(False)


def p_expression_identifier(p):
    """expression : IDENTIFIER"""
    p[0] = IdentifierNode(p[1])

def p_error(p):
    if p:
        print(f"  Syntax Error: Unexpected token '{p.value}' of type {p.type} at line {p.lineno}")
    else:
        print("  Syntax Error: Unexpected end of file")

def create_parser():
    return yacc.yacc(debug=False, write_tables=False)

def parse(source_code):
    lexer = create_lexer()
    parser = create_parser()
    return parser.parse(source_code, lexer=lexer)

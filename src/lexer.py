import ply.lex as lex

reserved = {
    'mutghyr': 'MUTGHYR',
    'sahih': 'SAHIH',
    'ashri': 'ASHRI',
    'nass': 'NASS',
    'mantqi': 'MANTQI',
    'sawab': 'TRUE',
    'khata': 'FALSE',
    'idha': 'IDHA',
    'wala': 'WALA',
    'talama': 'TALAMA',
    'utbaa': 'UTBAA',
    'dalah': 'DALAH',
    'irjaa': 'IRJAA',
    'wa': 'WA',
    'aw': 'AW',
    'lays': 'LAYS',
}


tokens = [
    'IDENTIFIER', 'INTEGER', 'FLOAT_NUM', 'STRING',
    'PLUS', 'MINUS', 'TIMES', 'DIVIDE', 'MODULO',
    'EQ', 'NEQ', 'LT', 'GT', 'LTE', 'GTE',
    'ASSIGN',
    'LPAREN', 'RPAREN', 'LBRACE', 'RBRACE',
    'SEMICOLON', 'COMMA', 'COLON',
] + list(reserved.values())

t_EQ      = r'=='
t_NEQ     = r'!='
t_LTE     = r'<='
t_GTE     = r'>='
t_LT      = r'<'
t_GT      = r'>'
t_PLUS    = r'\+'
t_MINUS   = r'-'
t_TIMES   = r'\*'
t_DIVIDE  = r'/'
t_MODULO  = r'%'
t_ASSIGN  = r'='
t_LPAREN  = r'\('
t_RPAREN  = r'\)'
t_LBRACE  = r'\{'
t_RBRACE  = r'\}'
t_COLON   = r':'


def t_SEMICOLON(t):
    r"""[;\u061b]"""
    return t


def t_COMMA(t):
    r"""[,\u060c]"""
    return t


def t_FLOAT_NUM(t):
    r"""\d+\.\d+"""
    t.value = float(t.value)
    return t


def t_INTEGER(t):
    r"""\d+"""
    t.value = int(t.value)
    return t


def t_STRING(t):
    r'''"[^"]*"'''
    t.value = t.value[1:-1]
    return t


def t_IDENTIFIER(t):
    r"""[a-zA-Z_\u0620-\u06FF\u0750-\u077F\u08A0-\u08FF\uFB50-\uFDFF\uFE70-\uFEFF][a-zA-Z0-9_\u0620-\u06FF\u0750-\u077F\u08A0-\u08FF\uFB50-\uFDFF\uFE70-\uFEFF]*"""
    t.type = reserved.get(t.value, 'IDENTIFIER')
    return t


def t_COMMENT(t):
    r"""(\#|//)[^\n]*"""
    pass


def t_newline(t):
    r"""\n+"""
    t.lexer.lineno += len(t.value)


t_ignore = ' \t\r'


def t_error(t):
    print(f"  Lexical Error: Unexpected character '{t.value[0]}' at line {t.lexer.lineno}")
    t.lexer.skip(1)

def create_lexer():
    return lex.lex()


def tokenize(source_code):
    lexer = create_lexer()
    lexer.input(source_code)
    tokens_list = []
    while True:
        tok = lexer.token()
        if not tok:
            break
        tokens_list.append(tok)
    return tokens_list

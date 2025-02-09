import ply.lex as lex
import ply.yacc as yacc
from graphviz import Digraph

# === Лексический анализатор (TOKENIZER) ===
tokens = (
    "ID",
    "NUMBER",
    "ASSIGN",
    "INCREMENT",
    "DECREMENT",
    "LPAREN",
    "RPAREN",
    "LBRACE",
    "RBRACE",
    "SEMICOLON",
    "LESS",
)

reserved = {"int": "INT", "do": "DO", "while": "WHILE"}
tokens += tuple(reserved.values())

# Регулярные выражения для токенов
t_ASSIGN = r"="
t_INCREMENT = r"\+\+"
t_DECREMENT = r"--"
t_LPAREN = r"\("
t_RPAREN = r"\)"
t_LBRACE = r"\{"
t_RBRACE = r"\}"
t_SEMICOLON = r";"
t_LESS = r"<"

t_ignore = " \t"


def t_ID(t):
    r"[a-zA-Z_][a-zA-Z0-9_]*"
    t.type = reserved.get(t.value, "ID")
    return t


def t_NUMBER(t):
    r"\d+"
    t.value = int(t.value)
    return t


def t_newline(t):
    r"\n+"
    t.lexer.lineno += len(t.value)


def t_error(t):
    print(f"Illegal character '{t.value[0]}' at line {t.lineno}")
    t.lexer.skip(1)


lexer = lex.lex()


# === Синтаксический анализатор (PARSER) ===
class ASTNode:
    """Узел AST-дерева"""

    def __init__(self, name, children=None):
        self.name = name
        self.children = children if children else []

    def add_child(self, child):
        self.children.append(child)


def p_program(p):
    """program : statement
    | statement program
    | empty"""
    if len(p) == 2:
        p[0] = ASTNode("Program", [p[1]])
    else:
        p[0] = p[2]
        p[0].children.insert(0, p[1])


def p_statement(p):
    """statement : declaration
    | assignment
    | increment
    | decrement
    | do_while"""
    p[0] = p[1]


def p_declaration(p):
    """declaration : INT ID SEMICOLON"""
    p[0] = ASTNode(f"Declaration ({p[2]})")


def p_assignment(p):
    """assignment : ID ASSIGN expression SEMICOLON"""
    p[0] = ASTNode(f"Assign ({p[1]} = {p[3]})")


def p_increment(p):
    """increment : ID INCREMENT SEMICOLON"""
    p[0] = ASTNode(f"Increment ({p[1]}++)")


def p_decrement(p):
    """decrement : ID DECREMENT SEMICOLON"""
    p[0] = ASTNode(f"Decrement ({p[1]}--)")


def p_expression(p):
    """expression : ID
    | NUMBER
    | ID LESS NUMBER"""
    p[0] = ASTNode(f"{p[1]} < {p[3]}" if len(p) > 2 else str(p[1]))


def p_do_while(p):
    """do_while : DO LBRACE program RBRACE WHILE LPAREN expression RPAREN SEMICOLON"""
    p[0] = ASTNode("Do-While", [p[3], ASTNode(f"Condition ({p[7]})")])


def p_empty(p):
    """empty :"""
    p[0] = ASTNode("Empty")


def p_error(p):
    if p:
        print(f"Syntax error at '{p.value}', line {p.lineno}")
    else:
        print("Syntax error: unexpected end of input")


parser = yacc.yacc()


# === Функция для создания AST-графа ===
def build_ast_graph(node, graph=None, parent=None):
    if graph is None:
        graph = Digraph()

    node_id = str(id(node))
    graph.node(node_id, node.name)

    if parent:
        graph.edge(parent, node_id)

    for child in node.children:
        build_ast_graph(child, graph, node_id)

    return graph


# === Тестовый запуск ===
cpp_code = """
int a; 
a = 5;
do {
    a++;
} while (a < 10);
"""

print("\n🔍 Разбор C++ кода...")
ast_root = parser.parse(cpp_code)

if ast_root:
    print("\n✅ Синтаксический анализ успешно завершён!")
    ast_graph = build_ast_graph(ast_root)
    ast_graph.render("syntax_tree", format="png", view=True)

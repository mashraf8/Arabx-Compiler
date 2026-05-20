from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.tree import Tree
from rich.text import Text
from rich import box
from src.ast_nodes import *
import sys, io, os

if sys.platform == 'win32':
    if not isinstance(sys.stdout, io.TextIOWrapper) or sys.stdout.encoding != 'utf-8':
        try:
            sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
        except Exception:
            pass

console = Console(force_terminal=True)


def print_phase_header(phase_num, arabic_title, english_title):
    console.print()
    console.print(Panel(
        f"[bold white]{english_title}[/]",
        title=f"[bold cyan]═══ Phase {phase_num} ═══[/]",
        border_style="bright_cyan",
        padding=(1, 2),
    ))


def print_source_code(source):
    console.print(Panel(
        source.strip(),
        title="[bold green]Source Code[/]",
        border_style="green",
    ))

def print_tokens(tokens_list):
    print_phase_header(1, "", "Lexical Analysis")

    table = Table(
        title="[bold]Token Table[/]",
        box=box.ROUNDED,
        header_style="bold magenta",
        show_lines=True,
    )
    table.add_column("#", style="dim", justify="center", width=4)
    table.add_column("Token Type", style="cyan", justify="center")
    table.add_column("Value", style="green", justify="center")
    table.add_column("Line", style="yellow", justify="center")

    for i, tok in enumerate(tokens_list, 1):
        table.add_row(
            str(i),
            str(tok.type),
            str(tok.value),
            str(tok.lineno),
        )

    console.print(table)
    console.print(f"  [bold green]✓[/] Total tokens: [bold]{len(tokens_list)}[/]")

def print_ast(ast_node):
    print_phase_header(2, "", "Syntax Analysis")

    tree = Tree("[bold yellow] Abstract Syntax Tree (AST)[/]")
    _build_tree(tree, ast_node)
    console.print(tree)
    console.print("  [bold green]✓[/] AST built successfully")


def _build_tree(tree, node):
    if node is None:
        return

    if isinstance(node, ProgramNode):
        prog = tree.add("[bold blue]Program[/]")
        for stmt in node.statements:
            _build_tree(prog, stmt)

    elif isinstance(node, DeclarationNode):
        decl = tree.add(f"[bold green]Declaration: {node.name} : {node.var_type}[/]")
        val = decl.add("[yellow]Value[/]")
        _build_tree(val, node.value)

    elif isinstance(node, AssignmentNode):
        assign = tree.add(f"[bold green]Assignment: {node.name}[/]")
        val = assign.add("[yellow]Value[/]")
        _build_tree(val, node.value)

    elif isinstance(node, PrintNode):
        pr = tree.add("[bold magenta]Print[/]")
        _build_tree(pr, node.expression)

    elif isinstance(node, IfNode):
        if_node = tree.add("[bold red]If[/]")
        cond = if_node.add("[yellow]Condition[/]")
        _build_tree(cond, node.condition)
        body = if_node.add("[green]Then[/]")
        _build_tree(body, node.if_body)
        if node.else_body:
            else_b = if_node.add("[red]Else[/]")
            _build_tree(else_b, node.else_body)

    elif isinstance(node, WhileNode):
        wh = tree.add("[bold red]While[/]")
        cond = wh.add("[yellow]Condition[/]")
        _build_tree(cond, node.condition)
        body = wh.add("[green]Body[/]")
        _build_tree(body, node.body)

    elif isinstance(node, FunctionDeclNode):
        func = tree.add(f"[bold cyan]Function: {node.name} → {node.return_type}[/]")
        if node.params:
            params = func.add("[yellow]Params[/]")
            for pname, ptype in node.params:
                params.add(f"{pname}: {ptype}")
        body = func.add("[green]Body[/]")
        _build_tree(body, node.body)

    elif isinstance(node, ReturnNode):
        ret = tree.add("[bold red]Return[/]")
        _build_tree(ret, node.expression)

    elif isinstance(node, BlockNode):
        for stmt in node.statements:
            _build_tree(tree, stmt)

    elif isinstance(node, BinaryOpNode):
        op = tree.add(f"[bold white]BinaryOp: {node.op}[/]")
        left = op.add("[cyan]Left[/]")
        _build_tree(left, node.left)
        right = op.add("[cyan]Right[/]")
        _build_tree(right, node.right)

    elif isinstance(node, UnaryOpNode):
        un = tree.add(f"[bold white]UnaryOp: {node.op}[/]")
        _build_tree(un, node.operand)

    elif isinstance(node, NumberNode):
        tree.add(f"[blue]Number: {node.value}[/]")

    elif isinstance(node, FloatNode):
        tree.add(f"[blue]Float: {node.value}[/]")

    elif isinstance(node, StringNode):
        tree.add(f'[blue]String: "{node.value}"[/]')

    elif isinstance(node, BoolNode):
        tree.add(f"[blue]Bool: {node.value}[/]")

    elif isinstance(node, IdentifierNode):
        tree.add(f"[yellow]Identifier: {node.name}[/]")

    elif isinstance(node, FunctionCallNode):
        call = tree.add(f"[bold magenta]Call: {node.name}()[/]")
        for arg in node.args:
            a = call.add("[cyan]Arg[/]")
            _build_tree(a, arg)

def print_semantic_results(analyzer):
    """Print semantic analysis results"""
    print_phase_header(3, "", "Semantic Analysis")

    if analyzer.errors:
        for err in analyzer.errors:
            console.print(f"  [bold red]✗[/] {err}")
    else:
        console.print("  [bold green]✓[/] No semantic errors - analysis passed")

def print_intermediate_code(instructions):
    """Print Three-Address Code"""
    print_phase_header(4, "", "Intermediate Code Generation (TAC)")

    console.print("[bold]Three-Address Code:[/]")
    console.print("─" * 50)
    for i, instr in enumerate(instructions):
        line = str(instr)
        if instr.op == 'LABEL':
            console.print(f"[bold yellow]{line}[/]")
        elif instr.op in ('FUNC_BEGIN', 'FUNC_END'):
            console.print(f"[bold cyan]{line}[/]")
        elif instr.op in ('GOTO', 'IF_TRUE', 'IF_FALSE'):
            console.print(f"[bold red]{line}[/]")
        else:
            console.print(f"[white]{line}[/]")
    console.print("─" * 50)
    console.print(f"  [bold green]✓[/] Total instructions: [bold]{len(instructions)}[/]")

def print_target_code(assembly_lines):
    """Print generated assembly code"""
    print_phase_header(5, "", "Target Code Generation (x86 Assembly)")

    code = "\n".join(assembly_lines)
    console.print(Panel(
        code,
        title="[bold green]x86 Assembly Output[/]",
        border_style="green",
    ))
    console.print(f"  [bold green]✓[/] Total assembly lines: [bold]{len(assembly_lines)}[/]")

def print_compilation_summary(success):
    """Print final compilation summary"""
    console.print()
    if success:
        console.print(Panel(
            "[bold green]✓ Compilation completed successfully![/]",
            title="[bold green]Final Result[/]",
            border_style="green",
            padding=(1, 2),
        ))
    else:
        console.print(Panel(
            "[bold red]✗ Compilation failed with errors[/]",
            title="[bold red]Final Result[/]",
            border_style="red",
            padding=(1, 2),
        ))

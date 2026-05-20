"""
Arabic Language Compiler
"""
import sys
import os
import io

if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
    os.environ['PYTHONIOENCODING'] = 'utf-8'

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.lexer import tokenize
from src.parser_module import parse
from src.semantic import SemanticAnalyzer
from src.intermediate import IntermediateCodeGenerator
from src.codegen import TargetCodeGenerator
from src.interpreter import Interpreter
from src import logger


def compile_arabic(source_code, source_name="<input>"):
    from rich.console import Console
    from rich.panel import Panel
    console = Console()

    console.print()
    console.print(Panel(
        "[bold white]Arabic Language Compiler[/] [bold cyan]Arabi[/]\n"
        "[dim]Arabic Language Compiler v1.0[/]",
        title="[bold cyan]═══ Compiler ═══[/]",
        border_style="bright_cyan",
        padding=(1, 3),
    ))

    logger.print_source_code(source_code)

    success = True

    tokens_list = tokenize(source_code)
    logger.print_tokens(tokens_list)

    if not tokens_list:
        console.print("[bold red]  ✗ No tokens found![/]")
        logger.print_compilation_summary(False)
        return

    ast = parse(source_code)
    if ast is None:
        console.print("[bold red]  ✗ Syntax analysis failed![/]")
        logger.print_compilation_summary(False)
        return
    logger.print_ast(ast)

    analyzer = SemanticAnalyzer()
    sem_ok = analyzer.analyze(ast)
    logger.print_semantic_results(analyzer)

    if not sem_ok:
        success = False
        logger.print_compilation_summary(False)
        return

    icg = IntermediateCodeGenerator()
    tac_instructions = icg.generate(ast)
    logger.print_intermediate_code(tac_instructions)

    codegen = TargetCodeGenerator()
    assembly = codegen.generate(tac_instructions)
    logger.print_target_code(assembly)

    logger.print_compilation_summary(success)

    if success:
        console.print()
        interpreter = Interpreter()
        try:
            output = interpreter.interpret(ast)
            console.print(Panel(
                "\n".join(output) if output else "[dim](no output)[/]",
                title="[bold bright_green]>>> Program Output <<<[/]",
                border_style="bright_green",
                padding=(1, 3),
            ))
        except Exception as e:
            console.print(Panel(
                f"[bold red]Runtime Error:[/] {e}",
                title="[bold red]>>> Execution Failed <<<[/]",
                border_style="red",
                padding=(1, 3),
            ))


def main():
    """Main entry point"""
    if len(sys.argv) > 1:
        filepath = sys.argv[1]
        if os.path.isfile(filepath):
            with open(filepath, 'r', encoding='utf-8') as f:
                source = f.read()
            compile_arabic(source, filepath)
        else:
            print(f"Error: File not found: {filepath}")
            sys.exit(1)
    else:
        print("Error: No input file provided.")
        print("Usage: python src/arabx.py <path_to_file.arabx>")
        sys.exit(1)


if __name__ == '__main__':
    main()

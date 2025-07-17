import typer
from typing_extensions import Annotated
from pathlib import Path
from sys import exit

from .mariachi import run

app = typer.Typer()

# ANSI escape codes for styling
RESET = "\033[0m"
BOLD = "\033[1m"

# Color codes
RED = "\033[91m"
GREEN = "\033[92m"
GREY = "\033[90m"

# Styled text formats
TITLE = f"{BOLD}{RED}"
SUBTITLE = f"{GREEN}"
PROMPT = f"{RED}mariachi{RESET} > "
intro = f"{RED}Saludos desde el Mariachi REPL!{RESET}\n"
intro += f"{GREEN}Type 'salir' to quit.{RESET}\n"


@app.command()
def main(
    debug: Annotated[bool, typer.Option(help="Run the Mariachi Repl in Debug Mode.")] = False,
    repl: Annotated[bool, typer.Option(help="Run the Mariachi Repl.")] = False,
    file: Annotated[
        Path,
        typer.Option(
            exists=True,
            readable=True,
            writable=False,
            dir_okay=False,
            file_okay=True,
            help="File with your Mariachi script",
        ),
    ] = None,
):
    if repl:
        run_repl()
    elif debug:
        debug_repl()
    else:
        run_script(file)


def run_script(
    file,
):
    """Run a Mariachi script from a file."""
    try:
        code = file.read_text()
        result, error = run(file, code)
        if error:
            print(error.as_string())
        elif result:
            if len(result.elements) == 1:
                print(str(result.elements[0]))
            else:
                print(str(result))
    except Exception as e:
        print(f"{e}")


def debug_repl():
    print(intro)
    while True:
        try:
            code = input(PROMPT)
            if code.strip() == "":
                continue
            if code == "salir" or code == "salir()":
                break
            elif not code:
                continue

            result, error = run("repl", code)

            if error:
                print(error.as_string())
            elif result:
                if len(result.elements) == 1:
                    print(repr(result.elements[0]))
                else:
                    print(repr(result))
        except Exception as e:
            print(f"{e}")


def run_repl():
    print(intro)
    while True:
        code = input(PROMPT)
        if code.strip() == "":
            continue
        if code == "salir" or code == "salir()":
            break
        elif not code:
            continue

        result, error = run("repl", code)

        if error:
            print(error.as_string())
        elif result:
            if len(result.elements) == 1:
                print(str(result.elements[0]))
            else:
                print(str(result))


if __name__ == "__main__":
    app()

import typer
from pathlib import Path

from .mariachi import run, run_file

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


@app.command("run")
def run_script(
    file: Path = typer.Argument(..., help="Path to your Mariachi script"),
):
    """Run a Mariachi script from a file."""
    run_file(file)

@app.command("repl")
def start_repl():
    """Launch the interactive Mariachi REPL."""
    repl()


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

def repl():
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
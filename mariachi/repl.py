from .mariachi import run

RED = "\033[91m"
GREEN = "\033[92m"
GREY = "\033[90m"
BOLD = "\033[1m"
RESET = "\033[0m"
TITLE = f"{BOLD}{RED}"
SUBTITLE = f"{GREEN}"
PROMPT = f"{RED}mariachi{RESET} > "


def repl():
    print(f"{TITLE}Saludos desde el Mariachi REPL!{RESET}")
    print(f"{SUBTITLE}Type 'salir' to quit.{RESET}\n")
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
                print(repr(result.elements[0]))
            else:
                print(repr(result))


if __name__ == "__main__":
    repl()

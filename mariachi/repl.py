"""REPL for the Mariachi toy language."""

from .parser import run

def repl():
    print("Saludos desde el Mariachi REPL!")
    print("Type 'exit()' to quit.\n")
    while True:
        code = input("mariachi > ")
        if code == "exit()":
            break
        elif not code:
            continue
        
        result, error = run('repl', code)

        if error:
            print(error.as_string())
        else:
            print(result)

if __name__ == "__main__":
    repl()
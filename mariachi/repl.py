"""REPL for the Mariachi toy language."""

def repl():
    print("Saludos desde el Mariachi REPL!")
    print("Type 'exit()' to quit.\n")
    while True:
        code = input("mariachi > ")

        if code == "exit()":
            break
        elif not code:
            continue

if __name__ == "__main__":
    repl()
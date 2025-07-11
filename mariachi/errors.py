class Error:
    """The custom error classes of the Mariachi Lang."""
    def __init__(self, pos_start, pos_end, error_name, details):
        self.pos_start = pos_start
        self.pos_end = pos_end
        self.error_name = error_name
        self.details = details

    def as_string(self):
        """Converts our error type into a string with provided details."""
        result = f'{self.error_name}: {self.details}'
        result += f'\nFile {self.pos_start.fn}, line {self.pos_end.ln} + 1'
        result += '\n' + string_with_arrows(self.pos_start.ftxt, self.pos_start, self.pos_end)
        return result
    
class InesperadoError(Error):
    def __init__(self, pos_start, pos_end, details):
        """Subclass for unexpected character inputs."""
        super().__init__(pos_start, pos_end, 'Caracter Inesperado', details)

class SintaxisInvalidoError(Error):
    def __init__(self, pos_start, pos_end, details=''):
        super().__init__(pos_start, pos_end, 'Sintaxis Invalido', details)

class EjecucionError(Error):
    def __init__(self, pos_start, pos_end, details, context):
        super().__init__(pos_start, pos_end, 'Ejecucion error', details)
        self.context = context

    def as_string(self):
        result  = self.generate_traceback()
        result += f'{self.error_name}: {self.details}'
        result += '\n' + string_with_arrows(self.pos_start.ftxt, self.pos_start, self.pos_end)
        return result

class CaracterEsperadoError(Error):
    def __init__(self, pos_start, pos_end, details):
        super().__init__(pos_start, pos_end, 'Caracter esperado', details)

    def as_string(self):
        """Custom method to represent errors as strings."""
        result = self.generate_traceback()
        result += f'{self.error_name}: {self.details}'
        result += '\n' + string_with_arrows(self.pos_start.ftxt, self.pos_start, self.pos_end)
        return result

    def generate_traceback(self):
        """Generates a traceback for error handling."""
        result = ''
        pos = self.pos_start
        ctx = self.context

        while ctx:
            result = f' Fichero {pos.fn}, lina {str(pos.ln + 1)}, en {ctx.display_name}\n'
            pos = ctx.parent_entry_pos
            ctx = ctx.parent
        return 'Retrazo (funcion mas reciente):\n' + result

def string_with_arrows(code, pos_start, pos_end):
    """Adds arrows to point to where the error occured."""
    YELLOW = "\033[93m"
    BOLD = '\033[1m'
    RESET = '\033[0m'
    # Holds our final result
    result = ''

    # Calculates indices
    idx_start = max(code.rfind('\n', 0, pos_start.idx), 0)
    idx_end = code.find('\n', idx_start + 1)
    if idx_end < 0:
        idx_end = len(code)

    # Generate each line
    line_count = pos_end.ln - pos_start.ln + 1
    for i in range(line_count):
        line = code[idx_start:idx_end]
        col_start = pos_start.col if i == 0 else 0
        col_end = pos_end.col if i == line_count - 1 else len(line) - 1

        # Append to result
        num_arrows = max(1, col_end - col_start)
        result += f"{BOLD}{line}{RESET}\n"
        result += ' ' * col_start + f"{YELLOW}{'^' * num_arrows}{RESET}"

        # Recalculate indices
        idx_start = idx_end
        idx_end = code.find('\n', idx_start + 1)
        if idx_end < 0: idx_end = len(code)
    return result.replace('\t', '')

def format_lines(lines):
    new_line = "### cactus ###"
    empty_line = "\n"

    if lines[-1].startswith(new_line):
        return False, lines
    else:
        return True, lines + [empty_line, new_line, empty_line]
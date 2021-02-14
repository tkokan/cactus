import sqlparse


def format_lines(lines):

    separator = "\n"
    input_query = separator.join(lines)

    parsed = sqlparse.parse(input_query)

    first, second = parsed

    for token in second.tokens:
        print(f"{type(token)} :: {token}")


    print("#")

    # if lines[-1].startswith(new_line):
    #     return False, lines
    # else:
    #     return True, lines + [empty_line, new_line, empty_line]
import argparse
import sys
from typing import Optional, Sequence, Dict, Any


def _build_arg_parser() -> argparse.ArgumentParser:
    
    parser = argparse.ArgumentParser(
        description="SQL code formatter"
        " "
        "https://github.com/tkokan/cactus"
    )

    inline_args_group = parser.add_mutually_exclusive_group()
    
    parser.add_argument(
        "-c",
        "--check-only",
        "--check",
        action="store_true",
        dest="check",
        help="Checks the file for unformatted code and prints info to the "
        "command line without modifying the file."
    )

    parser.add_argument(
        "-d",
        "--stdout",
        help="Force resulting output to stdout, instead of in-place.",
        dest="write_to_stdout",
        action="store_true"
    )

    parser.add_argument(
        "-i",
        "--indent",
        help='String to place for indents defaults to "  " (2 spaces).',
        dest="indent",
        type=str,
        default="  "
    )

    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        dest="verbose",
        help="Shows verbose output, such as when files are skipped or when a check is successful."
    )
    
    parser.add_argument(
        "-l",
        "-w",
        "--line-length",
        "--line-width",
        help="The max length of SQL code line.",
        dest="line_length",
        type=int,
        default=88
    )

    parser.add_argument(
        "files", nargs="*", help="One or more SQL source files that need to be formatted."
    )

    return parser


def parse_args(argv: Optional[Sequence[str]] = None) -> Dict[str, Any]:
    argv = sys.argv[1:] if argv is None else list(argv)

    parser = _build_arg_parser()
    arguments = {key: value for key, value in vars(parser.parse_args(argv)).items() if value}
    
    return arguments


def main(argv: Optional[Sequence[str]] = None) -> None:
    arguments = parse_args(argv)
    pass

if __name__ == "__main__":
    main()

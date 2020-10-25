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
    
    file_names = arguments.pop("files", [])
    
    config_dict = arguments.copy()
    check = config_dict.pop("check", False)

    skipped: List[str] = []
    broken: List[str] = []

    file_names = iter_source_code(file_names, config, skipped, broken)

    num_skipped = 0
    num_broken = 0
    num_invalid_encoding = 0

    attempt_iterator = (
        sort_imports(
            file_name,
            config=config,
            check=check,
            ask_to_apply=ask_to_apply,
            show_diff=show_diff,
            write_to_stdout=write_to_stdout,
        )
        for file_name in file_names
    )

    # If any files passed in are missing considered as error, should be removed
    is_no_attempt = True
    any_encoding_valid = False
    for sort_attempt in attempt_iterator:
        if not sort_attempt:
            continue  # pragma: no cover - shouldn't happen, satisfies type constraint
        incorrectly_sorted = sort_attempt.incorrectly_sorted
        if arguments.get("check", False) and incorrectly_sorted:
            wrong_sorted_files = True
        if sort_attempt.skipped:
            num_skipped += (
                1  # pragma: no cover - shouldn't happen, due to skip in iter_source_code
            )

        if not sort_attempt.supported_encoding:
            num_invalid_encoding += 1
        else:
            any_encoding_valid = True

        is_no_attempt = False

    num_skipped += len(skipped)
    if num_skipped and not arguments.get("quiet", False):
        if config.verbose:
            for was_skipped in skipped:
                warn(
                    f"{was_skipped} was skipped as it's listed in 'skip' setting"
                    " or matches a glob in 'skip_glob' setting"
                )
        print(f"Skipped {num_skipped} files")

    num_broken += len(broken)
    if num_broken and not arguments.get("quite", False):
        if config.verbose:
            for was_broken in broken:
                warn(f"{was_broken} was broken path, make sure it exists correctly")
        print(f"Broken {num_broken} paths")

    if num_broken > 0 and is_no_attempt:
        all_attempt_broken = True
    if num_invalid_encoding > 0 and not any_encoding_valid:
        no_valid_encodings = True

    if wrong_sorted_files:
        sys.exit(1)

    if all_attempt_broken:
        sys.exit(1)


if __name__ == "__main__":
    main()

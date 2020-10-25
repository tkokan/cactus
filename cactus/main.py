import argparse
import sys
from typing import Optional, Sequence, Dict, Any
from . import api, sections


class FormatAttempt:
    def __init__(self, needs_formatting: bool, skipped: bool, supported_encoding: bool) -> None:
        self.needs_formatting = needs_formatting
        self.skipped = skipped
        self.supported_encoding = supported_encoding


def format_sql(file_name: str, config: Config, check: bool = False, **kwargs: Any) -> Optional[FormatAttempt]:

    needs_formatting: bool = False
    skipped: bool = False
    
    try:
        if check:
            try:
                needs_formatting = not api.check_file(file_name, config=config, **kwargs)
            except FileSkipped:
                skipped = True
            return FormatAttempt(needs_formatting, skipped, supported_encoding=True)

        try:
            needs_formatting = not api.format_file(file_name, config=config, **kwargs)
        except FileSkipped:
            skipped = True
        return FormatAttempt(incorrectly_sorted, skipped, supported_encoding=True)
    except (OSError, ValueError) as error:
        warn(f"Unable to parse file {file_name} due to {error}")
        return None
    except UnsupportedEncoding:
        if config.verbose:
            warn(f"Encoding not supported for {file_name}")
        return SortAttempt(incorrectly_sorted, skipped, supported_encoding=False)


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


def iter_source_code(
    paths: Iterable[str], config: Config, skipped: List[str], broken: List[str]
) -> Iterator[str]:
    """Iterate over all Python source files defined in paths."""
    visited_dirs: Set[Path] = set()

    for path in paths:
        if os.path.isdir(path):
            for dirpath, dirnames, filenames in os.walk(path, topdown=True, followlinks=True):
                base_path = Path(dirpath)
                for dirname in list(dirnames):
                    full_path = base_path / dirname
                    resolved_path = full_path.resolve()
                    if config.is_skipped(full_path):
                        skipped.append(dirname)
                        dirnames.remove(dirname)
                    else:
                        if resolved_path in visited_dirs:
                            if not config.quiet:
                                warn(f"Likely recursive symlink detected to {resolved_path}")
                            dirnames.remove(dirname)
                    visited_dirs.add(resolved_path)

                for filename in filenames:
                    filepath = os.path.join(dirpath, filename)
                    if config.is_supported_filetype(filepath):
                        if config.is_skipped(Path(filepath)):
                            skipped.append(filename)
                        else:
                            yield filepath
        elif not os.path.exists(path):
            broken.append(path)
        else:
            yield path


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
        format_sql(
            file_name,
            config=config,
            check=check
        )
        for file_name in file_names
    )

    # If any files passed in are missing considered as error, should be removed
    is_no_attempt = True
    any_encoding_valid = False

    for format_attempt in attempt_iterator:
        needs_formatting = format_attempt.needs_formatting
        if arguments.get("check", False) and needs_formatting:
            wrong_formatted_files = True
        if sort_attempt.skipped:
            num_skipped += 1

        if not format_attempt.supported_encoding:
            num_invalid_encoding += 1
        else:
            any_encoding_valid = True

        is_no_attempt = False

    num_skipped += len(skipped)
    if num_skipped:
        if config.verbose:
            for was_skipped in skipped:
                warn(
                    f"{was_skipped} was skipped as it's listed in 'skip' setting"
                    " or matches a glob in 'skip_glob' setting"
                )
        print(f"Skipped {num_skipped} files")

    num_broken += len(broken)
    if num_broken:
        if config.verbose:
            for was_broken in broken:
                warn(f"{was_broken} was broken path, make sure it exists correctly")
        print(f"Broken {num_broken} paths")

    if num_broken > 0 and is_no_attempt:
        all_attempt_broken = True
    if num_invalid_encoding > 0 and not any_encoding_valid:
        no_valid_encodings = True

    if wrong_formatted_files:
        sys.exit(1)

    if all_attempt_broken:
        sys.exit(1)

    if no_valid_encodings:
        print("No valid encodings.")
        sys.exit(1)

if __name__ == "__main__":
    main()

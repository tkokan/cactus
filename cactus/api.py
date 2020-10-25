from typing import Optional, TextIO, Union, cast
from pathlib import Path
from .formatter import format_lines
import os

def process_file(filename: Union[str, Path], check_only: bool = False) -> bool:
    
    with open(filename) as source_file:
        source_file = open(filename)
        source_lines = source_file.readlines()
        source_file_path = Path(os.path.realpath(source_file.name))

    changed, new_lines = format_lines(source_lines)

    if check_only or not changed:
        return changed

    tmp_file_path = source_file_path.with_suffix(source_file_path.suffix + ".cactus")

    with open(tmp_file_path, "w") as tmp_file:
        tmp_file.writelines(new_lines)

    tmp_file_path.replace(source_file_path)
    print(f"Fixing {source_file_path}")

    return True

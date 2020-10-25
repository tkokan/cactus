from typing import Optional, TextIO, Union, cast
from .formatter import format_lines

def check_file(
    filename: Union[str, Path],
    show_diff: Union[bool, TextIO] = False,
    config: Config = DEFAULT_CONFIG,
    file_path: Optional[Path] = None,
    disregard_skip: bool = True,
    extension: Optional[str] = None,
    **config_kwargs,
) -> bool:
    
    with io.File.read(filename) as source_file:
        changed, _ = format_lines(source_file.readlines())
    
        return changed

def format_file(
    filename: Union[str, Path],
    extension: Optional[str] = None,
    config: Config = DEFAULT_CONFIG,
    file_path: Optional[Path] = None,
    disregard_skip: bool = True,
    ask_to_apply: bool = False,
    show_diff: Union[bool, TextIO] = False,
    **config_kwargs
) -> bool:
    
    with io.File.read(filename) as source_file:
        actual_file_path = file_path or source_file.path
        config = _config(path=actual_file_path, config=config, **config_kwargs)
        changed: bool = False
        tmp_file = source_file.path.with_suffix(source_file.path.suffix + ".cactus")

        try:
            with tmp_file.open("w", encoding=source_file.encoding, newline="") as output_stream:
                shutil.copymode(filename, tmp_file)
                
                changed, new_lines = format_lines(source_file.readlines())

            if changed:
                source_file.stream.close()
                tmp_file.writelines(new_lines)
                tmp_file.replace(source_file.path)
                print(f"Fixing {source_file.path}")
        finally:
                try:
                    tmp_file.unlink()
                except FileNotFoundError:
                    pass

        return changed

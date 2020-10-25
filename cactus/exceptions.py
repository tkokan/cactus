from pathlib import Path
from typing import Any, Dict, Union


class CactusError(Exception):
    """Base cactus exception object from which all cactus sourced exceptions should inherit"""


class FileSkipped(CactusError):
    """Should be raised when a file is skipped for any reason"""

    def __init__(self, message: str, file_path: str):
        super().__init__(message)
        self.file_path = file_path


class UnsupportedEncoding(CactusError):
    """Raised when cactus encounters an encoding error while trying to read a file"""

    def __init__(
        self,
        filename: Union[str, Path],
    ):
        super().__init__(f"Unknown or unsupported encoding in {filename}")
        self.filename = filename
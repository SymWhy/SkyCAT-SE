# src/errors.py
from dataclasses import dataclass

# Base class for SkyCAT-SE errors
class SkycatError(Exception):
    def __str__(self) -> str:
        return f"SkyCAT-SE caught an error: {self}"

# Configuration problems (invalid `skycat.ini`).
@dataclass
class ConfigError(SkycatError):
    message: str

    def __str__(self) -> str:
        return self.message or f"The ini file is invalid."

# Problems with the cache files.
@dataclass
class CacheError(SkycatError):
    path: str
    message: str | None = None
    line: int | None = None

    def __str__(self) -> str:
        return self.message
    
@dataclass
class ReadError(SkycatError):
    path: str
    message: str

    def __str__(self) -> str:
        return self.message or f"File could not be read from {self.path}: {self.message}"

# Unexpected string in file. (while updating or building the cache)
@dataclass
class ParseError(SkycatError):
    path: str
    message: str

    def __str__(self) -> str:
        return self.message or f"Unexpected string or character in {self.path}: {self.message}"

# Problems with writing to disk.
@dataclass
class WriteError(SkycatError):
    path: str
    message: str

    def __str__(self) -> str:
        return self.message or f"Could not write to {self.path}: {self.message}"

# User cancelled operation.
class UserAbort(SkycatError):
    
    def __str__(self) -> str:
        return "Operation cancelled by user."
    
# User does something weird and not allowed.
class InvalidOperation(SkycatError):
    def __str__(self) -> str:
        return self.message or "The requested operation is invalid in the current context."
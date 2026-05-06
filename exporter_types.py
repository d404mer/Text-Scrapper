from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

    # дефолтные расширения для экспорта
DEFAULT_EXTENSIONS = {
    ".py",
    ".js",
    ".ts",
    ".tsx",
    ".jsx",
    ".java",
    ".kt",
    ".kts",
    ".c",
    ".h",
    ".cpp",
    ".hpp",
    ".cc",
    ".cs",
    ".go",
    ".rs",
    ".rb",
    ".php",
    ".swift",
    ".scala",
    ".m",
    ".mm",
    ".sh",
    ".bash",
    ".ps1",
    ".sql",
    ".r",
    ".dart",
    ".lua",
    ".pl",
}

# дефолтные директории для исключения из экспорта
DEFAULT_EXCLUDED_DIRS = {
    ".git",
    ".svn",
    ".hg",
    "node_modules",
    "venv",
    ".venv",
    "__pycache__",
    "dist",
    "build",
    ".idea",
    ".vscode",
}


@dataclass
class FileRecord:
    # описывает файл, который прошел фильтрацию и будет экспортирован
    rel_path: Path
    full_path: Path
    ext: str
    size: int


@dataclass
class SkipRecord:
    # хранит информацию о файлах, которые были пропущены
    rel_path: Path
    reason: str


@dataclass
class Stats:
    # собирает агрегированную статистику выполнения
    scanned_files: int = 0
    included_files: int = 0
    skipped_files: int = 0
    included_bytes: int = 0
    skipped_bytes: int = 0
    read_errors: int = 0


@dataclass
class ExportEntry:
    # финальный текстовый блок для конкретного файла
    rel_path: Path
    content: str


@dataclass
class ExportConfig:
    # объединяет все параметры запуска в единую структуру
    root: Path
    output: Path
    include_ext: set[str]
    exclude_dirs: set[str]
    gitignore_patterns: list[str]
    max_size_bytes: int
    dry_run: bool
    respect_gitignore: bool

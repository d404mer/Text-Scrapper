from __future__ import annotations

import fnmatch
from pathlib import Path
from typing import Iterable


def parse_csv_set(raw: str | None, *, lower: bool = False) -> set[str]:
    # разбирает аргумент csv в множество значений
    if not raw:
        return set()
    values = {item.strip() for item in raw.split(",") if item.strip()}
    if lower:
        return {v.lower() for v in values}
    return values


def normalize_extensions(exts: Iterable[str]) -> set[str]:
    # приводит расширения к нижнему регистру и формату с точкой
    normalized: set[str] = set()
    for item in exts:
        ext = item.strip().lower()
        if not ext:
            continue
        if not ext.startswith("."):
            ext = f".{ext}"
        normalized.add(ext)
    return normalized


def load_gitignore_patterns(root: Path) -> list[str]:
    # читает корневой .gitignore и возвращает простые паттерны
    gitignore = root / ".gitignore"
    if not gitignore.is_file():
        return []

    patterns: list[str] = []
    try:
        lines = gitignore.read_text(encoding="utf-8", errors="replace").splitlines()
    except OSError:
        return []

    for line in lines:
        value = line.strip()
        if not value or value.startswith("#"):
            continue
        if value.startswith("!"):
            continue
        patterns.append(value)
    return patterns


def is_ignored_by_gitignore(rel_path: Path, patterns: list[str]) -> bool:
    # проверяет путь на совпадение с паттернами .gitignore
    if not patterns:
        return False

    rel_posix = rel_path.as_posix()
    for pattern in patterns:
        normalized = pattern.replace("\\", "/")
        if normalized.endswith("/"):
            dir_prefix = normalized.rstrip("/")
            if rel_posix == dir_prefix or rel_posix.startswith(f"{dir_prefix}/"):
                return True
            continue

        if "/" in normalized:
            if fnmatch.fnmatch(rel_posix, normalized):
                return True
            continue

        parts = rel_path.parts
        if any(fnmatch.fnmatch(part, normalized) for part in parts):
            return True
        if fnmatch.fnmatch(rel_posix, normalized):
            return True
    return False

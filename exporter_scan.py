from __future__ import annotations

import os
from argparse import Namespace
from pathlib import Path

from exporter_filters import (
    is_ignored_by_gitignore,
    load_gitignore_patterns,
    normalize_extensions,
    parse_csv_set,
)
from exporter_types import (
    DEFAULT_EXCLUDED_DIRS,
    DEFAULT_EXTENSIONS,
    ExportConfig,
    FileRecord,
    SkipRecord,
    Stats,
)


def resolve_config(args: Namespace) -> ExportConfig:
    # собирает конфиг запуска из аргументов cli
    root = Path(args.root).expanduser().resolve()
    output = Path(args.output).expanduser().resolve()
    include_ext = normalize_extensions(
        parse_csv_set(args.include_ext, lower=True) or DEFAULT_EXTENSIONS
    )
    exclude_dirs = DEFAULT_EXCLUDED_DIRS | parse_csv_set(args.exclude_dirs)
    gitignore_patterns = load_gitignore_patterns(root) if args.respect_gitignore else []
    return ExportConfig(
        root=root,
        output=output,
        include_ext=include_ext,
        exclude_dirs=exclude_dirs,
        gitignore_patterns=gitignore_patterns,
        max_size_bytes=args.max_size_kb * 1024,
        dry_run=args.dry_run,
        respect_gitignore=args.respect_gitignore,
    )


def validate_config(config: ExportConfig, max_size_kb: int) -> int | None:
    # валидирует корневую папку и ограничение размера
    if not config.root.exists() or not config.root.is_dir():
        print(f"Error: root directory does not exist or is not a directory: {config.root}")
        return 2
    if max_size_kb < 0:
        print("Error: --max-size-kb must be >= 0")
        return 2
    return None


def should_skip_by_gitignore(
    rel_path: Path, *, respect_gitignore: bool, patterns: list[str]
) -> bool:
    # применяет проверку .gitignore только если флаг включен
    return respect_gitignore and is_ignored_by_gitignore(rel_path, patterns)


def filter_walk_dirnames(
    dirnames: list[str],
    rel_dir: Path,
    *,
    exclude_dirs: set[str],
    respect_gitignore: bool,
    patterns: list[str],
) -> list[str]:
    # отфильтровывает поддиректории до входа в них
    filtered: list[str] = []
    for dirname in dirnames:
        if dirname in exclude_dirs:
            continue
        candidate_rel = rel_dir / dirname
        if should_skip_by_gitignore(
            candidate_rel, respect_gitignore=respect_gitignore, patterns=patterns
        ):
            continue
        filtered.append(dirname)
    return filtered


def collect_selected_files(
    config: ExportConfig, stats: Stats, skipped: list[SkipRecord]
) -> list[FileRecord]:
    # проходит по дереву проекта и выбирает подходящие файлы
    selected_files: list[FileRecord] = []
    for current_root, dirnames, filenames in os.walk(config.root):
        current_path = Path(current_root)
        rel_dir = current_path.relative_to(config.root)
        dirnames[:] = filter_walk_dirnames(
            dirnames,
            rel_dir,
            exclude_dirs=config.exclude_dirs,
            respect_gitignore=config.respect_gitignore,
            patterns=config.gitignore_patterns,
        )

        for filename in filenames:
            full_path = current_path / filename
            rel_path = full_path.relative_to(config.root)
            stats.scanned_files += 1

            if should_skip_by_gitignore(
                rel_path,
                respect_gitignore=config.respect_gitignore,
                patterns=config.gitignore_patterns,
            ):
                continue

            ext = full_path.suffix.lower()
            if ext not in config.include_ext:
                continue

            try:
                size = full_path.stat().st_size
            except OSError:
                stats.skipped_files += 1
                stats.read_errors += 1
                skipped.append(SkipRecord(rel_path, "read_error"))
                continue

            if size > config.max_size_bytes:
                stats.skipped_files += 1
                stats.skipped_bytes += size
                skipped.append(SkipRecord(rel_path, "skipped: file too large"))
                continue

            selected_files.append(
                FileRecord(rel_path=rel_path, full_path=full_path, ext=ext, size=size)
            )
            stats.included_files += 1
            stats.included_bytes += size
    return selected_files

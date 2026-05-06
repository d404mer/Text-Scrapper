#!/usr/bin/env python3
"""
Code exporter utility.

Recursively scans a project directory and writes a single dump file containing
source code files that match allowed extensions.
"""

from __future__ import annotations

import argparse
import sys
import time

from exporter_entries import build_export_entries
from exporter_output import ensure_output_parent, write_output
from exporter_scan import collect_selected_files, resolve_config, validate_config
from exporter_types import SkipRecord, Stats


def build_parser() -> argparse.ArgumentParser:
    # описывает cli-интерфейс утилиты
    parser = argparse.ArgumentParser(
        description="Export project source code files into one text dump."
    )
    parser.add_argument(
        "--root",
        default=".",
        help="Project root directory to scan (default: current directory).",
    )
    parser.add_argument(
        "--output",
        default="code_dump.txt",
        help="Output dump path: .txt or .docx (default: code_dump.txt).",
    )
    parser.add_argument(
        "--include-ext",
        default="",
        help="Comma-separated list of allowed extensions (e.g. .py,.js,.ts).",
    )
    parser.add_argument(
        "--exclude-dirs",
        default="",
        help="Comma-separated list of directories to exclude in addition to defaults.",
    )
    parser.add_argument(
        "--max-size-kb",
        type=int,
        default=1024,
        help="Maximum file size to include, in KB (default: 1024).",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print only files that would be included, without writing content.",
    )
    parser.add_argument(
        "--respect-gitignore",
        action="store_true",
        help="Skip files/dirs that match patterns from root .gitignore.",
    )
    return parser


def print_stats(stats: Stats, skipped: list[SkipRecord], elapsed_sec: float) -> None:
    # печатает итоговую статистику выполнения
    print("\n=== Statistics ===")
    print(f"Scanned files: {stats.scanned_files}")
    print(f"Included files: {stats.included_files}")
    print(f"Skipped files: {stats.skipped_files}")
    print(f"Included bytes: {stats.included_bytes}")
    print(f"Skipped bytes: {stats.skipped_bytes}")
    print(f"Read errors: {stats.read_errors}")
    print(f"Skip records: {len(skipped)}")
    print(f"Elapsed time: {elapsed_sec:.3f} sec")


def run_export(args: argparse.Namespace) -> int:
    # основной сценарий: конфиг, сканирование, экспорт, отчет
    start = time.perf_counter()
    config = resolve_config(args)

    validation_error = validate_config(config, args.max_size_kb)
    if validation_error is not None:
        return validation_error

    stats = Stats()
    skipped: list[SkipRecord] = []
    selected_files = collect_selected_files(config, stats, skipped)

    if config.dry_run:
        print("Dry-run: files that would be exported")
        for item in selected_files:
            print(item.rel_path.as_posix())
        elapsed = time.perf_counter() - start
        print_stats(stats, skipped, elapsed)
        return 0

    mkdir_error = ensure_output_parent(config.output)
    if mkdir_error is not None:
        return mkdir_error

    entries = build_export_entries(selected_files, stats, skipped)
    write_error = write_output(config.output, entries)
    if write_error is not None:
        return write_error

    elapsed = time.perf_counter() - start
    print(f"Export complete: {config.output}")
    print_stats(stats, skipped, elapsed)
    return 0


def main() -> int:
    # точка входа для запуска из консоли
    parser = build_parser()
    args = parser.parse_args()
    return run_export(args)


if __name__ == "__main__":
    sys.exit(main())

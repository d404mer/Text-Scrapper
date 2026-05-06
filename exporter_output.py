from __future__ import annotations

from pathlib import Path

from exporter_docx import write_docx_dump
from exporter_types import ExportEntry


def write_text_dump(output: Path, entries: list[ExportEntry]) -> None:
    # записывает экспорт в обычный текстовый файл
    with output.open("w", encoding="utf-8", newline="\n") as out_file:
        out_file.write("".join(entry.content for entry in entries))


def ensure_output_parent(output: Path) -> int | None:
    # создает директорию результата при необходимости
    try:
        output.parent.mkdir(parents=True, exist_ok=True)
    except OSError as exc:
        print(f"Error: cannot create output directory: {exc}")
        return 2
    return None


def write_output(output: Path, entries: list[ExportEntry]) -> int | None:
    # выбирает writer в зависимости от расширения результата
    try:
        if output.suffix.lower() == ".docx":
            write_docx_dump(output, entries)
        else:
            write_text_dump(output, entries)
    except OSError as exc:
        print(f"Error: cannot write output file: {exc}")
        return 2
    return None

from __future__ import annotations

from exporter_types import ExportEntry, FileRecord, SkipRecord, Stats


def normalize_newlines(content: str) -> str:
    # нормализует переносы строк в unix-формат
    normalized = content.replace("\r\n", "\n").replace("\r", "\n")
    if not normalized.endswith("\n"):
        normalized += "\n"
    return normalized


def format_file_block(rel_path: str, content: str) -> str:
    # формирует чистый блок: путь и полный текст файла
    normalized = normalize_newlines(content)
    return f"{rel_path}\n{normalized}\n"


def format_error_block(rel_path: str, marker: str) -> str:
    # формирует блок для файлов с ошибкой чтения
    return f"{rel_path}\n[{marker}]\n\n"


def read_file_content(source_path) -> tuple[str | None, str | None]:
    # читает файл в utf-8 с fallback на replace
    try:
        return source_path.read_text(encoding="utf-8"), None
    except UnicodeDecodeError:
        try:
            return source_path.read_text(encoding="utf-8", errors="replace"), None
        except OSError:
            return None, "read_error"
    except OSError:
        return None, "read_error"


def make_export_entry(item: FileRecord, content: str) -> ExportEntry:
    # собирает экспортную запись для успешно прочитанного файла
    body = format_file_block(item.rel_path.as_posix(), content)
    return ExportEntry(rel_path=item.rel_path, content=body)


def make_error_entry(item: FileRecord, marker: str) -> ExportEntry:
    # собирает экспортную запись для проблемного файла
    body = format_error_block(item.rel_path.as_posix(), marker)
    return ExportEntry(rel_path=item.rel_path, content=body)


def build_export_entries(
    selected_files: list[FileRecord], stats: Stats, skipped: list[SkipRecord]
) -> list[ExportEntry]:
    # конвертирует выбранные файлы в итоговые текстовые записи
    entries: list[ExportEntry] = []
    for item in selected_files:
        content, error = read_file_content(item.full_path)
        if error:
            entries.append(make_error_entry(item, error))
            stats.skipped_files += 1
            stats.read_errors += 1
            skipped.append(SkipRecord(item.rel_path, error))
            continue

        if content is None:
            entries.append(make_error_entry(item, "read_error"))
            stats.skipped_files += 1
            stats.read_errors += 1
            skipped.append(SkipRecord(item.rel_path, "read_error"))
            continue

        entries.append(make_export_entry(item, content))

    if skipped:
        for skip in skipped:
            entries.append(
                ExportEntry(
                    rel_path=skip.rel_path,
                    content=f"{skip.rel_path.as_posix()}\n[{skip.reason}]\n\n",
                )
            )
    return entries

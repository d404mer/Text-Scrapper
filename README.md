# Code Exporter

Утилита на Python для экспорта исходников проекта в единый файл (`.txt` или `.docx`).

## Что делает

- Рекурсивно обходит проект от корневой папки.
- Берет только файлы с разрешенными расширениями.
- Игнорирует служебные директории и слишком большие файлы.
- Не останавливается при ошибке чтения отдельного файла.
- Выводит итоговую статистику по обработке.

## Требования

- Python 3.10+
- Windows / Linux / macOS

## Запуск

```bash
python code_exporter.py --root D:\project --output dump.docx 
```

## Аргументы CLI

- `--root` - путь к корню проекта (по умолчанию `.`).
- `--output` - путь к файлу результата (`.txt` или `.docx`, по умолчанию `code_dump.txt`).
- `--include-ext` - список разрешенных расширений через запятую (например: `.py,.js,.ts`).
- `--exclude-dirs` - дополнительные исключаемые директории через запятую.
- `--max-size-kb` - лимит размера файла в KB (по умолчанию `1024`).
- `--dry-run` - показать только список файлов, без выгрузки контента.
- `--respect-gitignore` - учитывать паттерны из корневого `.gitignore`.

## Формат содержимого экспорта

Для каждого файла:

1. первая строка — относительный путь;
2. далее — полный текст файла со всеми переносами;
3. затем пустая строка-разделитель.

Если файл не удалось прочитать, добавляется запись:

```text
path/to/file.ext
[read_error]
```

Если файл пропущен по размеру:

```text
path/to/file.ext
[skipped: file too large]
```

## Особенности `.docx`

- Название каждого файла оформляется как `Heading 1` (для навигации в Word).
- Заголовок файла: `Times New Roman`, 14 pt.
- Содержимое файла: `Courier New`, 12 pt.
- Межстрочный интервал для содержимого: `1.0`.

## Расширения по умолчанию

`.py, .js, .ts, .tsx, .jsx, .java, .kt, .kts, .c, .h, .cpp, .hpp, .cc, .cs, .go, .rs, .rb, .php, .swift, .scala, .m, .mm, .sh, .bash, .ps1, .sql, .r, .dart, .lua, .pl`

## Исключаемые директории по умолчанию

`.git, .svn, .hg, node_modules, venv, .venv, __pycache__, dist, build, .idea, .vscode`

## Примеры

Сухой прогон:

```bash
python code_exporter.py --root . --dry-run
```

Экспорт в Word:

```bash
python code_exporter.py --root . --output dump.docx
```

Кастомные расширения:

```bash
python code_exporter.py --root . --include-ext .py,.md,.toml
```

Дополнительные исключения директорий:

```bash
python code_exporter.py --root . --exclude-dirs .next,.cache,tmp
```

С учетом `.gitignore`:

```bash
python code_exporter.py --root . --respect-gitignore
```

## Структура проекта

- `code_exporter.py` — точка входа CLI.
- `exporter_types.py` — модели и константы.
- `exporter_filters.py` — фильтры расширений и `.gitignore`.
- `exporter_scan.py` — обход директорий и отбор файлов.
- `exporter_entries.py` — чтение файлов и формирование блоков экспорта.
- `exporter_output.py` — запись результата (`txt/docx`).
- `exporter_docx.py` — генерация Word XML и стили.

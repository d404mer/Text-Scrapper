from __future__ import annotations

import zipfile
from pathlib import Path
from xml.sax.saxutils import escape

from exporter_types import ExportEntry


def get_docx_content_types_xml() -> str:
    # описывает типы частей внутри docx-контейнера
    return """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
  <Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>
  <Default Extension="xml" ContentType="application/xml"/>
  <Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/>
  <Override PartName="/word/styles.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.styles+xml"/>
</Types>
"""


def get_docx_root_relationships_xml() -> str:
    # связывает корневой пакет с основным документом
    return """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/>
</Relationships>
"""


def get_docx_document_relationships_xml() -> str:
    # связывает документ с файлом стилей
    return """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/styles" Target="styles.xml"/>
</Relationships>
"""


def get_docx_styles_xml() -> str:
    # задает стили heading 1 и базовые шрифты
    return """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:styles xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">
  <w:docDefaults>
    <w:rPrDefault>
      <w:rPr>
        <w:rFonts w:ascii="Times New Roman" w:hAnsi="Times New Roman" w:cs="Times New Roman"/>
      </w:rPr>
    </w:rPrDefault>
  </w:docDefaults>
  <w:style w:type="paragraph" w:default="1" w:styleId="Normal">
    <w:name w:val="Normal"/>
    <w:qFormat/>
  </w:style>
  <w:style w:type="paragraph" w:styleId="Heading1">
    <w:name w:val="heading 1"/>
    <w:basedOn w:val="Normal"/>
    <w:next w:val="Normal"/>
    <w:uiPriority w:val="9"/>
    <w:qFormat/>
    <w:pPr>
      <w:outlineLvl w:val="0"/>
    </w:pPr>
    <w:rPr>
      <w:rFonts w:ascii="Times New Roman" w:hAnsi="Times New Roman" w:cs="Times New Roman"/>
      <w:sz w:val="28"/>
      <w:szCs w:val="28"/>
    </w:rPr>
  </w:style>
</w:styles>
"""


def make_heading_paragraph(text: str) -> str:
    # генерирует заголовок файла для навигации в word
    heading_text = escape(text)
    return (
        "    <w:p>"
        "<w:pPr><w:pStyle w:val=\"Heading1\"/><w:outlineLvl w:val=\"0\"/></w:pPr>"
        "<w:r><w:rPr>"
        "<w:rFonts w:ascii=\"Times New Roman\" w:hAnsi=\"Times New Roman\" w:cs=\"Times New Roman\"/>"
        "<w:sz w:val=\"28\"/><w:szCs w:val=\"28\"/>"
        "</w:rPr>"
        f"<w:t xml:space=\"preserve\">{heading_text}</w:t>"
        "</w:r></w:p>"
    )


def make_code_paragraph(text: str) -> str:
    # генерирует строку кода с одинарным межстрочным интервалом
    display = " " if text == "" else text
    escaped_line = escape(display)
    return (
        "    <w:p>"
        "<w:pPr><w:spacing w:line=\"240\" w:lineRule=\"auto\" w:before=\"0\" w:after=\"0\"/></w:pPr>"
        "<w:r><w:rPr>"
        "<w:rFonts w:ascii=\"Courier New\" w:hAnsi=\"Courier New\" w:cs=\"Courier New\"/>"
        "<w:sz w:val=\"24\"/><w:szCs w:val=\"24\"/>"
        "</w:rPr>"
        f"<w:t xml:space=\"preserve\">{escaped_line}</w:t>"
        "</w:r></w:p>"
    )


def extract_entry_lines(entry: ExportEntry) -> list[str]:
    # отделяет путь файла от строк его содержимого
    normalized = entry.content.replace("\r\n", "\n").replace("\r", "\n")
    lines = normalized.split("\n")
    if lines and lines[0] == entry.rel_path.as_posix():
        lines = lines[1:]
    if lines and lines[-1] == "":
        lines = lines[:-1]
    return lines


def build_docx_paragraphs(entries: list[ExportEntry]) -> str:
    # собирает весь набор параграфов документа
    paragraph_parts: list[str] = []
    for entry in entries:
        paragraph_parts.append(make_heading_paragraph(entry.rel_path.as_posix()))
        for line in extract_entry_lines(entry):
            paragraph_parts.append(make_code_paragraph(line))
        paragraph_parts.append("    <w:p><w:r><w:t xml:space=\"preserve\"> </w:t></w:r></w:p>")
    return "\n".join(paragraph_parts)


def build_docx_document_xml(paragraphs_xml: str) -> str:
    # оборачивает параграфы в каркас word/document.xml
    return f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:document xmlns:wpc="http://schemas.microsoft.com/office/word/2010/wordprocessingCanvas"
 xmlns:mc="http://schemas.openxmlformats.org/markup-compatibility/2006"
 xmlns:o="urn:schemas-microsoft-com:office:office"
 xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships"
 xmlns:m="http://schemas.openxmlformats.org/officeDocument/2006/math"
 xmlns:v="urn:schemas-microsoft-com:vml"
 xmlns:wp14="http://schemas.microsoft.com/office/word/2010/wordprocessingDrawing"
 xmlns:wp="http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing"
 xmlns:w10="urn:schemas-microsoft-com:office:word"
 xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"
 xmlns:w14="http://schemas.microsoft.com/office/word/2010/wordml"
 xmlns:w15="http://schemas.microsoft.com/office/word/2012/wordml"
 xmlns:wpg="http://schemas.microsoft.com/office/word/2010/wordprocessingGroup"
 xmlns:wpi="http://schemas.microsoft.com/office/word/2010/wordprocessingInk"
 xmlns:wne="http://schemas.microsoft.com/office/word/2006/wordml"
 xmlns:wps="http://schemas.microsoft.com/office/word/2010/wordprocessingShape"
 mc:Ignorable="w14 w15 wp14">
  <w:body>
{paragraphs_xml}
    <w:sectPr>
      <w:pgSz w:w="11906" w:h="16838"/>
      <w:pgMar w:top="1440" w:right="1440" w:bottom="1440" w:left="1440" w:header="708" w:footer="708" w:gutter="0"/>
    </w:sectPr>
  </w:body>
</w:document>
"""


def write_docx_dump(output: Path, entries: list[ExportEntry]) -> None:
    # упаковывает xml-части в итоговый .docx zip-контейнер
    paragraphs_xml = build_docx_paragraphs(entries)
    document_xml = build_docx_document_xml(paragraphs_xml)

    with zipfile.ZipFile(output, "w", compression=zipfile.ZIP_DEFLATED) as docx:
        docx.writestr("[Content_Types].xml", get_docx_content_types_xml())
        docx.writestr("_rels/.rels", get_docx_root_relationships_xml())
        docx.writestr("word/document.xml", document_xml)
        docx.writestr("word/_rels/document.xml.rels", get_docx_document_relationships_xml())
        docx.writestr("word/styles.xml", get_docx_styles_xml())

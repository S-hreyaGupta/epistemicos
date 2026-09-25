#!/usr/bin/env python3
"""Extract readable text from a .docx, with no third-party dependencies.

    python _inbox\\docx_to_text.py <path-to-docx>

A .docx is a zip; the text lives in word/document.xml. This keeps paragraph
and table-cell boundaries, drops everything else, and writes a .txt beside
this script so it can be read directly.

Deliberately minimal. It is not a converter, it is a reader.
"""
from __future__ import annotations

import html
import re
import sys
import zipfile
from pathlib import Path

HERE = Path(__file__).resolve().parent


def to_text(xml: str) -> str:
    # Paragraph and row ends become newlines, cell ends become tabs, before
    # any tag stripping — otherwise every boundary in the document is lost
    # and the result is one unreadable line.
    xml = re.sub(r"</w:p>", "\n", xml)
    xml = re.sub(r"</w:tr>", "\n", xml)
    xml = re.sub(r"</w:tc>", "\t", xml)
    xml = re.sub(r"<w:br[^>]*/>", "\n", xml)
    xml = re.sub(r"<w:tab[^>]*/>", "    ", xml)
    text = re.sub(r"<[^>]+>", "", xml)
    text = html.unescape(text)
    # Collapse the blank runs docx leaves behind, keep real blank lines.
    text = re.sub(r"[ \t]+\n", "\n", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip() + "\n"


def main() -> int:
    if len(sys.argv) < 2:
        print("usage: python _inbox\\docx_to_text.py <path-to-docx>")
        return 2
    src = Path(sys.argv[1])
    if not src.exists():
        print(f"not found: {src}")
        return 2

    with zipfile.ZipFile(src) as z:
        names = z.namelist()
        if "word/document.xml" not in names:
            print(f"no word/document.xml in {src.name}; entries: {names[:8]}")
            return 1
        xml = z.read("word/document.xml").decode("utf-8", "replace")

    out = HERE / (src.stem.split("_", 1)[-1] + ".txt")
    out.write_text(to_text(xml), encoding="utf-8")
    print(f"wrote {out}")
    print(f"{len(out.read_text(encoding='utf-8').splitlines())} lines")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

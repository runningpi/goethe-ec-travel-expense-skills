"""First look at a trip folder: what is in it and what do the documents say?

  python inventory.py <trip folder> [--chars 1500]

For every file: type, pages, whether it is a (filled) PDF form, a short text excerpt and the
money amounts, dates, times and order/reference numbers found in it. Images and scanned PDFs
have no text - open those visually. Sub-folders named 'Archiv' are skipped.
"""
import argparse
import os
import re

import fitz

from common import ensure_utf8_stdout

AMOUNT = re.compile(r"(?<![\d.,])\d{1,3}(?:\.\d{3})*,\d{2}(?!\d)")
DATE = re.compile(r"\b\d{1,2}\.\d{1,2}\.(?:20)?\d{2}\b|\b\d{1,2}[-/][A-Za-z]{3}[-/]\d{4}\b")
TIME = re.compile(r"\b(?:[01]?\d|2[0-3]):[0-5]\d\b")
ORDER = re.compile(r"(?:Auftragsnummer|Rechnungsnummer|Rechnung Nr\.?|Invoice(?: No\.?| number)?|Order #?|"
                   r"Buchungsnummer|Reservierungsnummer|Bestellnummer)[:\s]*([A-Z0-9-]{5,})", re.I)
HINTS = {
    "db_invoice": ["DB Fernverkehr", "Rechnung"], "db_ticket": ["Online-Ticket"],
    "bahncard": ["BahnCard", "Gültigkeit: ab"], "application": ["Antrag auf Genehmigung einer Dienstreise"],
    "reimbursement_form": ["Reisekostenabrechnung"], "a1": ["Koordinierung der Systeme"],
    "bank_statement": ["IBAN", "Umsätze"], "agenda": ["Program", "Agenda", "Programm"],
}


def guess(text):
    return [k for k, words in HINTS.items() if all(w.lower() in text.lower() for w in words)]


def main():
    ensure_utf8_stdout()
    ap = argparse.ArgumentParser()
    ap.add_argument("folder")
    ap.add_argument("--chars", type=int, default=1200)
    a = ap.parse_args()
    for root, dirs, files in os.walk(a.folder):
        dirs[:] = [d for d in dirs if d.lower() != "archiv"]
        for f in sorted(files):
            path = os.path.join(root, f)
            rel = os.path.relpath(path, a.folder)
            ext = f.lower().rsplit(".", 1)[-1]
            print("=" * 100)
            print(rel, f"({os.path.getsize(path) // 1024} KB)")
            if ext in ("png", "jpg", "jpeg", "heic"):
                print("  IMAGE -> open it visually (screenshot of ticket / payment / receipt?)")
                continue
            if ext != "pdf":
                print("  other file type")
                continue
            try:
                doc = fitz.open(path)
            except Exception as e:
                print("  cannot open:", e)
                continue
            text = "\n".join(p.get_text() for p in doc)
            filled = [(w.field_name, w.field_value) for p in doc for w in p.widgets()
                      if w.field_value not in (None, "", "Off")]
            print(f"  pages={doc.page_count}  form={'yes' if doc.is_form_pdf else 'no'}"
                  f"  filled_fields={len(filled)}  text_chars={len(text)}  guess={guess(text)}")
            if len(text.strip()) < 50:
                print("  little/no text -> scanned or image PDF, open it visually")
            print("  amounts:", sorted(set(AMOUNT.findall(text)))[:25])
            print("  dates:  ", sorted(set(DATE.findall(text)))[:15])
            print("  times:  ", sorted(set(TIME.findall(text)))[:15])
            print("  refs:   ", sorted(set(ORDER.findall(text)))[:10])
            excerpt = re.sub(r"\s+", " ", text)[: a.chars]
            print("  text:", excerpt)


if __name__ == "__main__":
    main()

"""Find DB tickets booked with a BahnCard in any folder tree (works wherever the user keeps trips).

  python find_bahncard_tickets.py <folder> [<folder> ...] [--from 10.08.2026] [--to 09.08.2027]

Scans all PDFs (also inside Archiv folders) for DB online tickets that mention a BahnCard
("mit 1 BC50", "BC25", ...), and prints order number, fare, price, travel dates and the file.
Tickets that exist only as app screenshots (images) cannot be read here - they are listed as
"check visually". Duplicates (same order number in several files) are reported once.
"""
import argparse
import datetime
import os
import re

import fitz

from common import ensure_utf8_stdout

BC = re.compile(r"\bBC\s?(25|50|100)\b|BahnCard\s?(25|50|100)")
ORDER = re.compile(r"Auftragsnummer:?\s*(\d{9,})")
PRICE = re.compile(r"Gesamtpreis\s*([\d.]+,\d{2})")
FARE = re.compile(r"((?:Super )?Sparpreis[^\n(]*|Flexpreis[^\n(]*|Normalpreis[^\n(]*)")
TRAVEL = re.compile(r"(?:Zugbindung|Hinfahrt|Rückfahrt|Einfache Fahrt)[^\n]*?(\d{2}\.\d{2}\.\d{4})")
VALID = re.compile(r"Gültigkeit:\s*(\d{2}\.\d{2}\.\d{4})")
ROUTE = re.compile(r"(?:Hinfahrt|Einfache Fahrt)\s+(.+?)(?:\s+mit\s+\w+)?\n")


def d(s):
    return datetime.datetime.strptime(s, "%d.%m.%Y").date()


def main():
    ensure_utf8_stdout()
    ap = argparse.ArgumentParser()
    ap.add_argument("folders", nargs="+")
    ap.add_argument("--from", dest="start")
    ap.add_argument("--to", dest="end")
    a = ap.parse_args()
    seen, images = {}, []
    for folder in a.folders:
        for root, _, files in os.walk(folder):
            for f in files:
                path = os.path.join(root, f)
                low = f.lower()
                if low.endswith((".png", ".jpg", ".jpeg")) and any(k in low for k in ("ticket", "db", "bahn", "foto")):
                    images.append(path)
                if not low.endswith(".pdf"):
                    continue
                try:
                    text = "\n".join(p.get_text() for p in fitz.open(path))
                except Exception:
                    continue
                if "Online-Ticket" not in text or not BC.search(text):
                    continue
                order = (ORDER.search(text) or [None, "?"])[1]
                if order in seen:
                    continue
                dates = TRAVEL.findall(text) or VALID.findall(text)
                if a.start and dates and d(dates[0]) < d(a.start):
                    continue
                if a.end and dates and d(dates[0]) > d(a.end):
                    continue
                m = BC.search(text)
                seen[order] = {
                    "card": "BC" + (m.group(1) or m.group(2)),
                    "fare": (FARE.search(text) or [None, "?"])[1].strip(" ,"),
                    "price": (PRICE.search(text) or [None, "?"])[1],
                    "dates": ", ".join(dict.fromkeys(dates)),
                    "route": (ROUTE.search(text) or [None, ""])[1].strip(),
                    "file": path,
                }
    for order, t in sorted(seen.items(), key=lambda kv: d(kv[1]["dates"].split(",")[0]) if kv[1]["dates"] else datetime.date.min):
        print(f"{t['dates']:<24} {t['card']:<5} {t['price']:>8}  {t['fare']:<26} {t['route']:<45} order {order}\n    {t['file']}")
    if images:
        print("\nImages that may be ticket screenshots (check visually if a trip seems missing):")
        for p in images:
            print("   ", p)


if __name__ == "__main__":
    main()

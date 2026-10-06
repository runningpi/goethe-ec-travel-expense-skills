"""Make a redacted extract of a bank statement that only shows the bookings belonging to a trip.

  python redact_statement.py --pdf Kontoauszug.pdf --out 04_Kontoauszug_geschwaerzt_<Trip>.pdf \
      --keep "1052258685632" --keep "7 THINGS HOTEL" [--keep "page=17:1052546794870"] [--no-header] [--preview DIR]
  python redact_statement.py --pdf Kontoauszug.pdf --find 46,45      (search helper: where does a text occur?)

* Every --keep is a text that occurs in exactly one booking (best: an order/reference number;
  otherwise merchant name or amount). Without page= the statement is searched.
* The first page is added as a header page with everything below the account header blacked
  out, so the reviewer sees account holder + IBAN.
* Redaction removes the text (not just a black box) and the kept booking gets a red frame.
* Works on text-based PDFs (online banking exports). For scans or app screenshots, use the
  screenshot itself as proof of payment instead.
Always look at the --preview images before using the result: bank layouts differ.
"""
import argparse
import os
import re

import fitz

from common import ensure_utf8_stdout

# any money amount (balances included) marks the end of the account header
AMOUNT = re.compile(r"\d,\d{2}(?!\d)")
FOOTER_FRACTION = 0.91   # blocks below this share of the page height are footer (page number, bank slogan)


def left_blocks(page):
    return [b for b in page.get_text("blocks") if b[4].strip()]


def transaction_span(page, key):
    """Vertical extent of the booking containing `key`."""
    blocks = left_blocks(page)
    hits = [b for b in blocks if key in b[4]]
    if not hits:
        return None
    # prefer the left-most hit (description column), then widen to all blocks starting in its band
    b = sorted(hits, key=lambda b: b[0])[0]
    y0, y1 = b[1], b[3]
    for c in blocks:
        if c[1] >= y0 - 2 and c[1] <= y1 + 2:
            y1 = max(y1, c[3])
    return y0, y1


def redact(page, keep_spans, header=False):
    h = page.rect.height
    blocks = left_blocks(page)
    if header:
        amounts = [b[1] for b in blocks if AMOUNT.search(b[4])]
        cutoff = min(amounts) - 2 if amounts else h * 0.3
    for b in blocks:
        if b[1] >= h * FOOTER_FRACTION:
            continue
        if header and b[3] <= cutoff:
            continue
        if any(y0 - 2 <= b[1] <= y1 + 2 for y0, y1 in keep_spans):
            continue
        r = fitz.Rect(b[:4])
        page.add_redact_annot(fitz.Rect(r.x0 - 1, r.y0 - 1, r.x1 + 1, r.y1 + 1), fill=(0, 0, 0))
    page.apply_redactions(images=fitz.PDF_REDACT_IMAGE_NONE)
    w = page.rect.width
    for y0, y1 in keep_spans:
        page.draw_rect(fitz.Rect(w * 0.07, y0 - 6, w * 0.93, y1 + 6), color=(0.85, 0, 0), width=1.5)


def main():
    ensure_utf8_stdout()
    ap = argparse.ArgumentParser()
    ap.add_argument("--pdf", required=True)
    ap.add_argument("--out")
    ap.add_argument("--keep", action="append", default=[])
    ap.add_argument("--find")
    ap.add_argument("--no-header", action="store_true")
    ap.add_argument("--preview")
    a = ap.parse_args()
    src = fitz.open(a.pdf)

    if a.find:
        for i, p in enumerate(src):
            for b in left_blocks(p):
                if a.find in b[4]:
                    print(f"page {i + 1}: {b[4].strip()[:200]!r}")
        return

    # group keeps by page, keep order of first appearance
    pages = {}
    for k in a.keep:
        if k.startswith("page=") and ":" in k:
            pno, key = k[5:].split(":", 1)
            cand = [int(pno) - 1]
        else:
            key, cand = k, range(len(src))
        found = [(i, transaction_span(src[i], key)) for i in cand]
        found = [(i, s) for i, s in found if s]
        if len(found) != 1:
            raise SystemExit(f"--keep {k!r} matched {len(found)} bookings; use a more specific text or page=N:...")
        i, span = found[0]
        pages.setdefault(i, []).append(span)

    out = fitz.open()
    if not a.no_header:
        out.insert_pdf(src, from_page=0, to_page=0)
        redact(out[-1], pages.get(0, []), header=True)
    for i, spans in pages.items():
        if i == 0 and not a.no_header:
            continue
        out.insert_pdf(src, from_page=i, to_page=i)
        redact(out[-1], spans)
    out.save(a.out, garbage=4, deflate=True)
    print(f"Wrote {a.out} ({out.page_count} pages)")
    for n, p in enumerate(out):
        print(f"  page {n + 1}: {p.get_text().replace(chr(10), ' ')[:160]}")
        if a.preview:
            os.makedirs(a.preview, exist_ok=True)
            p.get_pixmap(dpi=60).save(os.path.join(a.preview, f"statement_p{n + 1}.png"))


if __name__ == "__main__":
    main()

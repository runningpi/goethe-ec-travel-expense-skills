"""Merge the filled form and all receipts into one PDF in the required order.

  python assemble.py --spec assemble.json --out 00_Abrechnung_<Name>_<Trip>_FINAL.pdf [--preview DIR]

assemble.json  (paths relative to the spec file's folder, or absolute):
[
  {"file": "01_Reiko_Abrechnung_SALTY.pdf"},
  {"file": "02_Dienstreiseantrag_SALTY.pdf"},
  {"file": "04_Kontoauszug_geschwaerzt.pdf", "pages": [1, 2]},
  {"images": ["Foto 1.png", "Foto 2.png"], "caption": "Zahlungsnachweis DB-Fahrkarten (2 x 15,74 EUR)"},
  {"file": "Agenda.pdf", "pages": [1, 7], "highlight": ["Jane Doe", "Title of my talk"]}
]
"highlight" marks texts (the user's name, the talk title) in yellow - the chair asks for the
own presentation to be marked in the programme. Long titles: pass a distinctive part of it.
Form fields and annotations are flattened, because merging two forms with the same field
names (e.g. 'Datum' exists in the reimbursement form and in the application) would
otherwise make the values overwrite each other.
"""
import argparse
import json
import os

import fitz

from common import ensure_utf8_stdout

A4 = fitz.paper_rect("a4")


def image_page(out, caption, images):
    page = out.new_page(width=A4.width, height=A4.height)
    top = 40
    if caption:
        # shrink long captions so they never run off the page
        size = 12
        while fitz.get_text_length(caption, fontname="helv", fontsize=size) > A4.width - 80 and size > 7:
            size -= 0.5
        page.insert_text((40, 50), caption, fontsize=size, fontname="helv")
        top = 70
    n = len(images)
    gap = 15
    box_w = (A4.width - 80 - gap * (n - 1)) / n
    for i, img in enumerate(images):
        x0 = 40 + i * (box_w + gap)
        page.insert_image(fitz.Rect(x0, top, x0 + box_w, A4.height - 40), filename=img, keep_proportion=True)


def main():
    ensure_utf8_stdout()
    ap = argparse.ArgumentParser()
    ap.add_argument("--spec", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--preview")
    a = ap.parse_args()
    base = os.path.dirname(os.path.abspath(a.spec))
    spec = json.load(open(a.spec, encoding="utf-8"))
    path = lambda p: p if os.path.isabs(p) else os.path.join(base, p)

    out = fitz.open()
    for item in spec:
        if "images" in item:
            image_page(out, item.get("caption", ""), [path(p) for p in item["images"]])
            continue
        f = path(item["file"])
        if f.lower().endswith((".png", ".jpg", ".jpeg")):
            image_page(out, item.get("caption", ""), [f])
            continue
        src = fitz.open(f)
        for term in item.get("highlight", []):
            hits = 0
            for pno in item.get("pages") or range(1, src.page_count + 1):
                quads = []
                # PDFs often use typographic quotes; also fall back to the first words of long titles
                for variant in (term, term.replace("'", "’"), " ".join(term.split()[:4])):
                    quads = src[pno - 1].search_for(variant, quads=True)
                    if quads:
                        break
                for quad in quads:
                    src[pno - 1].add_highlight_annot(quad)
                    hits += 1
            if not hits:
                print(f"WARNING: highlight text not found in {os.path.basename(f)}: {term!r}")
        if src.is_form_pdf or any(True for p in src for _ in p.annots()):
            src.bake()
        for pno in item.get("pages") or range(1, src.page_count + 1):
            out.insert_pdf(src, from_page=pno - 1, to_page=pno - 1)
    out.save(a.out, garbage=3, deflate=True)
    print(f"Wrote {a.out} ({out.page_count} pages)")
    if a.preview:
        os.makedirs(a.preview, exist_ok=True)
        for i, p in enumerate(out):
            p.get_pixmap(dpi=40).save(os.path.join(a.preview, f"page_{i + 1:02d}.png"))
        print(f"Preview images in {a.preview}")


if __name__ == "__main__":
    main()

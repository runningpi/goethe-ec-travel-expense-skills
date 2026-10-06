"""Shared helpers: config location, user profile, official form download, PDF form filling."""
import json
import os
import re
import sys
import urllib.request

import fitz  # PyMuPDF

# Everything personal lives outside the skill folder so the skill can be shared on GitHub.
HOME = os.environ.get("GOETHE_TRAVEL_HOME") or os.path.join(os.path.expanduser("~"), ".goethe-ec-travel-expenses")
PROFILE_PATH = os.path.join(HOME, "profile.json")
FORMS_DIR = os.path.join(HOME, "forms")

BASE = "https://www.uni-frankfurt.de"
# Official forms from the Formularcenter (https://www.uni-frankfurt.de/47065133/Formularcenter)
FORMS = {
    "reimbursement": BASE + "/48628954/reisekostenrechnung-pdf-mit-anlage.pdf",
    "application_domestic": BASE + "/70926891/antrag-auf-genehmigung-reisekosten20_02_18_inland.pdf",
    "application_abroad": BASE + "/178340204.pdf",
    "checklist": BASE + "/48628934/reisekostenabrechnung-_2_checkliste.pdf",
    "guidelines": BASE + "/48628978/reisekosten_merkblatt.pdf",
    "foreign_rates": BASE + "/182115660.pdf",
}


def ensure_utf8_stdout():
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass


def load_profile(required=True):
    if not os.path.exists(PROFILE_PATH):
        if required:
            sys.exit(f"No profile found at {PROFILE_PATH}. Run the setup first (scripts/setup_profile.py init).")
        return {}
    with open(PROFILE_PATH, encoding="utf-8") as f:
        return json.load(f)


def save_profile(profile):
    os.makedirs(HOME, exist_ok=True)
    with open(PROFILE_PATH, "w", encoding="utf-8") as f:
        json.dump(profile, f, ensure_ascii=False, indent=2)


def get_form(key, refresh=False):
    """Return a local path to an official form, downloading it into the cache if needed."""
    os.makedirs(FORMS_DIR, exist_ok=True)
    path = os.path.join(FORMS_DIR, key + ".pdf")
    if refresh or not os.path.exists(path):
        req = urllib.request.Request(FORMS[key], headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=60) as r, open(path, "wb") as f:
            f.write(r.read())
    return path


def money(x):
    """12.5 -> '12,50' (German decimal comma, thousands dot)."""
    s = f"{x:,.2f}"
    return s.replace(",", "X").replace(".", ",").replace("X", ".")


def parse_money(s):
    if isinstance(s, (int, float)):
        return float(s)
    s = str(s).strip().replace("EUR", "").replace("€", "").strip()
    if re.search(r",\d{1,2}$", s):
        s = s.replace(".", "").replace(",", ".")
    return float(s)


# Capital umlauts are missing from the embedded font subset of some fields in the
# university forms (e.g. "Österreich" renders as "sterreich"); lower-case ones work.
_SAFE = {"Ä": "Ae", "Ö": "Oe", "Ü": "Ue"}


def safe_text(v):
    return "".join(_SAFE.get(c, c) for c in str(v))


def set_radio(doc, page, field_name, index):
    """Select the radio option `index` (0 = left-most box) of `field_name`.

    Works on /AS and the parent /V directly: the export names in the university
    forms do not always match the printed labels (e.g. the left "ja" box of
    "Auszahlung Tagegeld" exports as "Nein"), so position is the only reliable key.
    """
    ws = sorted([w for w in page.widgets() if w.field_name == field_name], key=lambda w: (w.rect.x0, w.rect.y0))
    if not ws:
        raise KeyError(f"radio field not found: {field_name}")
    for i, w in enumerate(ws):
        on = w.on_state()
        if i == index:
            doc.xref_set_key(w.xref, "AS", f"/{on}")
            parent = doc.xref_get_key(w.xref, "Parent")
            if parent[0] == "xref":
                doc.xref_set_key(int(parent[1].split()[0]), "V", f"/{on}")
        else:
            doc.xref_set_key(w.xref, "AS", "/Off")


def fill_form(src, dst, text=None, checks=(), radios=None, fontsizes=None):
    """Fill an AcroForm PDF.

    text:   {field_name: value}
    checks: field names of check boxes to tick
    radios: {(page_index, field_name): option_index_from_left}
    fontsizes: {field_name: size}
    Unknown field names raise, so mapping mistakes surface immediately.
    """
    text = dict(text or {})
    radios = dict(radios or {})
    fontsizes = fontsizes or {}
    doc = fitz.open(src)
    seen = set()
    for page in doc:
        for w in page.widgets():
            n = w.field_name
            if w.field_type_string == "Text" and n in text:
                w.field_value = safe_text(text[n])
                if n in fontsizes:
                    w.text_fontsize = fontsizes[n]
                w.update()
                seen.add(n)
            elif w.field_type_string == "CheckBox" and n in checks:
                w.field_value = w.on_state()
                w.update()
                seen.add(n)
    for (pno, name), idx in radios.items():
        set_radio(doc, doc[pno], name, idx)
        seen.add(name)
    missing = (set(text) | set(checks) | {n for _, n in radios}) - seen
    if missing:
        raise KeyError(f"fields not found in {os.path.basename(src)}: {sorted(missing)}")
    doc.save(dst, garbage=3, deflate=True)
    return dst


def list_fields(path):
    doc = fitz.open(path)
    out = []
    for i, page in enumerate(doc):
        for w in page.widgets():
            out.append({
                "page": i + 1, "type": w.field_type_string, "name": w.field_name,
                "value": w.field_value, "rect": [round(v) for v in w.rect],
                "on_state": w.on_state() if w.field_type_string in ("CheckBox", "RadioButton") else None,
            })
    return out

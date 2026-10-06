"""Create / inspect the personal profile used for every travel report.

  python setup_profile.py init --from <old reimbursement or application PDF> [...]
  python setup_profile.py show
  python setup_profile.py set key=value [key=value ...]     (dotted keys allowed: bahncard.number=...)

`init` reads the form fields of a previously filled form (Reisekostenrechnung or
Dienstreiseantrag) and prints what it found. Fields it cannot find stay empty and
must be asked from the user. Nothing is written into the skill folder.
"""
import argparse
import json
import sys

import fitz

from common import PROFILE_PATH, ensure_utf8_stdout, load_profile, save_profile

TEMPLATE = {
    "name": "",               # "Lastname, Firstname" as on the forms
    "display_name": "",       # "Firstname Lastname" (annex page, letters)
    "phone": "",
    "institute": "Electronic Commerce",
    "department": "FB 02 / Marketing",
    "department_long": "02 / Marketing / Electronic Commerce",   # Dienstreiseantrag
    "address": "",            # private address
    "iban": "",
    "bank": "",
    "default_cost_center": "",  # the chair's default cost centre (ask the user)
    "cost_centers": [],          # [{"id": "...", "label": "Chair budget", "rule": "default"}, ...]
    "position": "Wissenschaftliche/r Mitarbeiter/in; Lehrstuhl Electronic Commerce, FB 02 Wirtschaftswissenschaften; Goethe-Universität",
    "workplace": "Goethe-Universität Frankfurt, Theodor-W.-Adorno-Platz 4, 60323 Frankfurt am Main",
    "social_security_number": "",   # Renten-/Sozialversicherungsnummer, only needed for trips abroad (A1)
    "health_insurance": "gesetzlich",  # gesetzlich | privat
    "pension_fund_member": False,
    "bahncard": {"type": "", "number": "", "valid_from": "", "valid_to": "", "price": ""},
}

# field name in the official forms -> profile key
FROM_REIMBURSEMENT = {
    "Name, Vorname": "name", "Telefonnummer": "phone", "Institut / Abteilung": "institute",
    "FB/Bereich": "department", "Adresse": "address", "Bankleitzahl": "iban", "Bankinstitut": "bank",
    "KostenstelleProjekt": "seen_cost_center",
}
FROM_APPLICATION = {
    "Antragstellerin  Name Vorname": "name", "AntragsstellerIn Name, Vorname": "name",
    "FachbereichInstitutAbteilung": "department_long", "Fachbereich/Institut/Abteilung": "department_long",
    "Telefon": "phone", "Sozialversicherungsnummer": "social_security_number",
    "Die Reise wird aus ProjektKostenstelle bezahlt": "seen_cost_center",
    "Projekt/Kostenstelle": "seen_cost_center",
}


def extract(path):
    found = {}
    doc = fitz.open(path)
    for page in doc:
        for w in page.widgets():
            if w.field_type_string != "Text" or not w.field_value:
                continue
            key = FROM_REIMBURSEMENT.get(w.field_name) or FROM_APPLICATION.get(w.field_name)
            if key and not found.get(key):
                found[key] = str(w.field_value).strip()
    if not found:
        print("No filled form fields found (the PDF is probably flattened or scanned). "
              "Read it visually and enter the values with `setup_profile.py set`.", file=sys.stderr)
    return found


def main():
    ensure_utf8_stdout()
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    p_init = sub.add_parser("init")
    p_init.add_argument("--from", dest="sources", nargs="*", default=[])
    sub.add_parser("show")
    p_set = sub.add_parser("set")
    p_set.add_argument("pairs", nargs="+")
    a = ap.parse_args()

    if a.cmd == "init":
        prof = load_profile(required=False) or json.loads(json.dumps(TEMPLATE))
        seen_cc = []
        for src in a.sources:  # earlier sources win; never overwrite values already in the profile
            for k, v in extract(src).items():
                if k == "seen_cost_center":
                    seen_cc.append(v)
                elif not prof.get(k):
                    prof[k] = v
        if prof.get("name") and not prof.get("display_name") and "," in prof["name"]:
            last, first = [s.strip() for s in prof["name"].split(",", 1)]
            prof["display_name"] = f"{first} {last}"
        save_profile(prof)
        print(f"Saved profile to {PROFILE_PATH}")
        print(json.dumps(prof, ensure_ascii=False, indent=2))
        if seen_cc:
            print("\nCost centers used on the old forms (confirm with the user which ones to keep):",
                  ", ".join(dict.fromkeys(seen_cc)))
        empty = [k for k, v in prof.items() if v in ("", None)]
        if empty:
            print("\nStill empty (ask the user):", ", ".join(empty))
    elif a.cmd == "show":
        print(json.dumps(load_profile(), ensure_ascii=False, indent=2))
    elif a.cmd == "set":
        prof = load_profile(required=False) or json.loads(json.dumps(TEMPLATE))
        for pair in a.pairs:
            k, v = pair.split("=", 1)
            try:
                v = json.loads(v)
            except ValueError:
                pass
            node = prof
            parts = k.split(".")
            for p in parts[:-1]:
                node = node.setdefault(p, {})
            node[parts[-1]] = v
        save_profile(prof)
        print(json.dumps(prof, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()

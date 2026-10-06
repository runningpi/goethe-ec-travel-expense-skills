---
name: travel-setup
description: One-time setup of the personal travel profile (name, IBAN, address, cost centres, BahnCard, data for A1 requests) used by the Chair of Electronic Commerce travel skills (/create-travel-application, /create-reimbursement, /bahncard-reimbursement), and home of their shared scripts and rules. Use it when someone sets up, checks or changes their travel/Reisekosten profile, changes bank account or address, or when another travel skill finds no profile yet.
---

# Travel profile setup (Chair of Electronic Commerce, Goethe University)

This skill does two things:
1. Creates/updates the personal profile all travel skills read
   (`~/.goethe-ec-travel-expenses/profile.json`, outside any repo or shared folder).
2. Holds the shared tools of the travel skills: `scripts/` and `references/` in this folder.
   The other skills refer to it as `<travel-setup>` = the sibling folder `../travel-setup`
   of their own skill folder.

Talk to the user in English unless they write German. Python 3 with `pymupdf openpyxl pillow`
is needed (`pip install pymupdf openpyxl pillow` if an import fails).

## Setup flow
1. `python <travel-setup>/scripts/setup_profile.py show` — if a profile exists, show it and ask
   what should change; otherwise continue.
2. Ask for one previous **filled** Reisekostenabrechnung and/or Dienstreiseantrag (PDF) and run
   `setup_profile.py init --from <pdf> [<pdf>]`. It reads name, phone, institute, address,
   IBAN, bank and lists the cost centres used before. If the PDF is flattened or scanned,
   read it visually and set values with `setup_profile.py set key=value`.
3. Ask once, in one message, for what is still missing and useful:
   - which project cost centres they use besides 102 103 17 and when (e.g. "ERC-PoC Data
     Market 3502030005 – only for ERC-related trips"); store as
     `cost_centers=[{"id": ..., "label": ..., "rule": ...}]`
   - BahnCard: type, number, validity, price (`bahncard.type=...` etc.) — skip if none
   - for trips abroad: pension/social insurance number, health insurance (gesetzlich/privat),
     position (pre-filled for research assistants of the chair)
   Nothing else; do not ask for signatures.
4. Show the final profile, say where it is stored and that it never leaves their computer.
5. **Next steps:** tell the user the commands they can use now:
   - `/create-travel-application` — before a trip
   - `/create-reimbursement <trip folder>` — after a trip
   - `/bahncard-reimbursement` — once their BahnCard savings exceed its price

## Shared resources (for the other travel skills)
| File | Content |
|---|---|
| `scripts/setup_profile.py` | profile init/show/set |
| `scripts/inventory.py` | overview of a trip folder (text, amounts, dates, order numbers) |
| `scripts/fill_application.py` | domestic/abroad travel application |
| `scripts/fill_reimbursement.py` | Reisekostenrechnung incl. annex |
| `scripts/redact_statement.py` | redacted bank-statement extract |
| `scripts/assemble.py` | merge into the final PDF, highlight own talk in the programme |
| `scripts/organize.py` | rename/archive files (dry run first) |
| `scripts/find_bahncard_tickets.py` | find BahnCard tickets in any folder tree |
| `scripts/bahncard.py` | BahnCard savings table + letter |
| `references/rules.md` | reimbursement rules (university Merkblatt) + chair conventions |
| `references/documents.md` | required documents, completeness check, PDF order, folder scheme |
| `references/chair-procedure.md` | chair procedure (signatures, A1 e-mail, in-house mail), next steps |

Official forms are downloaded on first use from the university Formularcenter and cached
in `~/.goethe-ec-travel-expenses/forms/` (`common.py` has the URLs; delete the cache to
refresh after the university publishes a new version).

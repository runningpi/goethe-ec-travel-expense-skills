---
name: create-reimbursement
description: Turns a folder with all documents of a past business trip into a complete, submission-ready travel expense claim (Reisekostenabrechnung) for the Chair of Electronic Commerce at Goethe University — domestic or abroad: reads tickets, invoices and screenshots, finds payment proofs in bank statements and redacts them, fetches the agenda, asks for anything missing, fills the official form and merges everything in the required order. Use it whenever someone wants to settle, file, prepare or check travel expenses, Reisekosten, Reiko, a Dienstreise or conference trip reimbursement, or points at a folder of travel receipts.
---

# Create a travel expense claim (after the trip)

Shared tools live in the sibling skill folder `../travel-setup` (called `<travel-setup>`):
scripts in `<travel-setup>/scripts` (each documents its JSON input in its docstring — read
it before writing the JSON), rules in `<travel-setup>/references`:
`rules.md` (what is reimbursable), `documents.md` (required documents, completeness table,
PDF order, folder scheme), `chair-procedure.md` (signatures, submission, next steps).

Talk to the user in English unless they write German; values on the form stay German.
**Never sign anything.** BahnCard reimbursement is **not** part of this skill — only mention
`/bahncard-reimbursement` if the user brings it up.

## 1. Profile and folder
- `python <travel-setup>/scripts/setup_profile.py show`; no profile → setup from
  `<travel-setup>/SKILL.md` first.
- The trip folder is the argument the user gave (`/create-reimbursement <folder>`); if none,
  ask for it. Folder locations differ between users — never assume a path.
- Check the 6-month deadline (end of trip + 6 months) and warn if it is close or passed.

## 2. Understand the trip
1. `python <travel-setup>/scripts/inventory.py "<folder>"`. Open every image and every PDF with
   little text visually.
2. From the approved application: destination, purpose, dates, cost centre.
3. List the cost items: what, amount, date, how it was paid, which file is invoice / payment
   proof / ticket. A return ticket is one item; hotel only for business nights.
4. Payment proofs: invoices marked paid (DB "Zahlung … PayPal", "PAID", "Saldo 0,00") are ok;
   otherwise ask where the bank statement export is (once) and search it with
   `redact_statement.py --pdf <statement> --find "<amount or order no>"`. Watch for PayPal
   "pay later" bookings weeks later with a different reference and for **refunds**
   ("Erstattung" + invoice number) — a refunded item is not claimed (ask if unsure).
   Banking-app screenshots of a single booking are fine as they are.
5. Agenda: if missing, find the programme on the event website and download/print it. Keep
   only overview pages + the page(s) with the user's session for long programmes.

## 3. Completeness check — ask before building
Show the table from `documents.md` (item | invoice | payment proof | ticket | status) and, in
the same message, your proposed answers for what documents can't show, asking the user to
confirm or correct:
- cost centre (default vs. project, rules.md §7)
- role: talk / poster / discussant / participant (if they presented, the programme gets their
  name and title marked)
- free meals (from the agenda: lunches, dinners; hotel breakfast on the invoice)
- trip start/end times if no ticket shows them; business start/end from the agenda
- private extension, cancellation, costs paid by others (rules.md §5)
Wait for the answer. Missing documents the user cannot provide → note them in the remarks
only if the user agrees to submit without them.

## 4. Build the claim
1. **Form:** write `trip.json` (docstring of `fill_reimbursement.py`) and create
   `01_Reiko_Abrechnung_<Trip>.pdf`. Keep remarks to ~2 lines (role, private part,
   cancellation, items paid by others, how hotel amount was derived). Hotel > 80 €/night
   (domestic) → annex reasons; taxi → annex + reason. Compare the printed total with the sum
   of the receipts.
2. **Bank statement:** `redact_statement.py --pdf ... --out NN_Kontoauszug_geschwaerzt_<Trip>.pdf
   --keep <ref> ... --preview <tmp>` and look at the previews (only account header + the trip's
   bookings readable, balance blacked out).
3. **Assemble:** `assemble.json` in the order of `documents.md`; for the programme add
   `"highlight": ["<user's name>", "<talk title>"]` if they presented. Run
   `assemble.py --preview <tmp>` → `00_Abrechnung_<Lastname>_<Trip>_FINAL.pdf`.
4. **Verify:** render pages 1–3 and skim the previews: ja/nein boxes, amounts, total, cost
   centre, no overflowing text, page order. Fix and re-run.

## 5. Tidy the folder (propose → confirm → apply)
Propose the renaming/archiving plan (`documents.md` scheme: `00_…_FINAL.pdf`, numbered
receipts in PDF order, unused files to `Archiv/`, other sub-folders untouched) as a short
list; after the user agrees run `organize.py --plan plan.json --apply`. Nothing is deleted.

## 6. Report and next steps (always)
Summarise: final PDF path, total amount, cost centre, assumptions made, anything excluded and
why. Then the numbered next steps from `chair-procedure.md`:
1. Check the PDF.
2. Print it, sign page 1 and the annex (page 3).
3. Chair holder checks and signs "sachlich richtig"; dean's office signs.
4. All originals in an envelope via in-house mail to Finanzabteilung / Reisekostenabrechnung,
   PF 52.
5. Deadline: <end of trip + 6 months>.

---
name: bahncard-reimbursement
description: Checks whether a privately bought BahnCard (25/50) has paid off through business trips and, if so, prepares its reimbursement for members of the Chair of Electronic Commerce at Goethe University — finds all tickets booked with the card in the user's trip folders, computes the savings table, writes the request letter and attaches everything to a travel claim. Use it when someone asks about BahnCard reimbursement, BahnCard Erstattung, whether their BahnCard is worth claiming, or how much they saved with it on Dienstreisen.
---

# BahnCard reimbursement

Shared tools live in the sibling skill folder `../travel-setup` (`<travel-setup>`); the
rule is in `<travel-setup>/references/rules.md` §6. Talk to the user in English unless they
write German. Never sign anything. Works on any computer — always ask where things are.

## 1. Card data
From the profile (`setup_profile.py show` → `bahncard`) or the BahnCard invoice the user
points to: type (25/50), number, price, purchase date, validity. Ask for the invoice file and
the payment proof (bank statement or screenshot) — both are attachments. Missing number:
ask (it is in the DB app under "BahnCard").

## 2. Collect business tickets booked with this card
Ask which folder(s) contain the user's business-trip documents (any location, any depth),
then run
`python <travel-setup>/scripts/find_bahncard_tickets.py <folder> [...] --from <valid from> --to <valid to>`.
It lists PDF tickets with the BahnCard mark, fare, price and dates. Tickets that only exist
as app screenshots are listed as images — open them. Count only tickets that
- were booked with **this** card type ("mit 1 BC50" for a BahnCard 50),
- were travelled within the card's validity,
- belong to business trips (also trips that were cancelled but had to be paid).
Show the list and let the user confirm or add trips.

## 3. Compute and decide
Write `bahncard.json` (docstring of `<travel-setup>/scripts/bahncard.py`) and run it into the
folder the user chooses (suggest a `BahnCard` folder next to their trip folders). It writes
the letter (unsigned), the overview table (xlsx + pdf) and prints savings vs. price.
- Savings ≤ price → not reimbursable yet; say how much is missing and that later trips within
  the validity count. Stop here.
- Savings > price → continue.

## 4. Attach to a claim
Ask which trip's claim the BahnCard should go with (usually the trip that pushed the savings
over the price) and which cost centre — the letter's cost centre must match that claim; if
the claim is already final, rebuild it:
- in that trip's `trip.json`: add the BahnCard price to `costs.other` and a short remark
  ("Sonstiges: BahnCard <type> (<price> EUR), Ersparnis <x> EUR – siehe Anlage"),
- append to the end of its `assemble.json`: letter → table PDF → BahnCard invoice →
  redacted payment proof (`redact_statement.py`),
- re-run `fill_reimbursement.py` and `assemble.py` (see the /create-reimbursement skill).
If the user prefers, the BahnCard can also be claimed on its own claim form with only
"sonstiges" filled.

## 5. Next steps (always)
1. Check the table and letter; sign the letter.
2. Sign the claim it is attached to; chair holder signs "sachlich richtig", dean's office signs.
3. Submit with that claim via in-house mail (Finanzabteilung / Reisekostenabrechnung, PF 52).
4. One BahnCard can only be reimbursed once — keep the overview with the trip.

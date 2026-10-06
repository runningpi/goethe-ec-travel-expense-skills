# Required documents, order and naming

## What the user puts into the trip folder
One folder per trip (e.g. `2026 SALTY Leuven/`), containing everything related to it — the
user does not need to sort or rename anything:

| Needed | Typical files |
|---|---|
| Approved application | `Dienstreiseantrag_*.pdf` (signed by the supervisor) |
| A1 certificate (abroad only) | PDF from HR, often with a cryptic name like `1105...}HTML000012.pdf` |
| Train | DB invoice (`DB_Invoice_*`, `DB Rechnung *`) **and** ticket (`DB_Ticket_*` or app screenshot) |
| Local transport | receipts / tickets (VGN, bus), card screenshots |
| Hotel | hotel **invoice** (not just the booking confirmation) |
| Conference fee | invoice / receipt of payment, ticket or registration |
| Payment proofs | for everything not already marked as paid on the invoice: bank statement (PDF export), banking-app screenshots |
| Agenda | programme of the event (download it if missing) |

Bank statements may live in a central folder (e.g. `Kontoauszüge/`); ask for the path once.

## Completeness check (before filling anything)
For every cost item the claim needs **invoice + proof of payment + ticket/evidence of the
service**, plus once per trip the **approved application** and an **agenda**.

A DB invoice that lists "Zahlung … PayPal/Kreditkarte" counts as paid, but the user prefers
the bank booking as additional proof when available. "PAID"/"Saldo 0,00" on a hotel or
conference invoice counts as proof too. Present a short table to the user:

| Item | Invoice | Payment proof | Ticket/evidence | Status |

and ask in **one** message for everything missing (application, tickets, payment proofs,
times, which cost centre, meals received, private parts of the trip). Only proceed with gaps
the user explicitly accepts.

Things to always confirm with the user (they are not visible in documents):
- cost centre (default vs. project, see rules.md §7)
- free meals received (conference lunches/dinners, hotel breakfast) — check the agenda and
  hotel invoice and propose an answer
- whether the user presented / was discussant / only attended (goes into remarks)
- private extensions, cancellations, refunds, costs paid by others
- start/end time of the trip if no ticket shows them (the user may give a rule like "22:00 if
  unknown")

## Order of the final PDF (`00_Abrechnung_<Name>_<Trip>_FINAL.pdf`)
1. Reisekostenrechnung (3 pages incl. Anlage) — filled
2. Approved application (Dienstreiseantrag) — all pages
3. A1 certificate (abroad only)
4. For each cost item, in this order: train → local transport → hotel → conference fee →
   other; each as **invoice → payment proof → ticket/evidence**
   (redacted bank-statement header page once, before the first statement extract)
5. Agenda / programme (only the relevant pages if it is long: overview + the page with the
   user's name/session)
6. BahnCard reimbursement if attached to this trip: letter → overview table → BahnCard
   invoice → payment proof

Don't include: booking confirmations when an invoice exists, refunded items, private
costs, internal attendee lists with personal data of others, registration confirmations
when a receipt of payment exists.

## Folder clean-up (propose, then apply after the user agrees)
```
2026 SALTY Leuven/
├── 00_Abrechnung_<Lastname>_<Trip>_FINAL.pdf
├── 01_Reiko_Abrechnung_<Trip>.pdf             (filled, still editable)
├── 02_Dienstreiseantrag_<Trip>.pdf
├── 03_A1_Bescheinigung_<Trip>.pdf
├── 04_DB_Rechnung_<ordernumber>.pdf
├── 05_Kontoauszug_geschwaerzt_<Trip>.pdf
├── 06_DB_Ticket_<ordernumber>.pdf
├── 07_Hotelrechnung_<Hotel>.pdf
├── ...
├── 09_Agenda_<Event>.pdf
└── Archiv/            (booking confirmations, blank templates, refunded items, old drafts)
```
Numbers follow the order inside the final PDF. Descriptive ASCII names (ue/ae/oe instead of
umlauts). Sub-folders with other content (photos, paper reviews, slides) stay untouched.
Never delete anything — unused files go to `Archiv/`.

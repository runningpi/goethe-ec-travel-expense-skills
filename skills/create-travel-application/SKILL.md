---
name: create-travel-application
description: Creates the travel application (Antrag auf Genehmigung einer Dienstreise) for a domestic or foreign business trip of a member of the Chair of Electronic Commerce at Goethe University, and for trips abroad drafts the A1-certificate request e-mail. Use it whenever someone plans a conference trip, workshop, research visit or other Dienstreise, needs a Reiseantrag / Dienstreisegenehmigung / travel approval, or asks what to do before travelling — even if they only say "I'm going to <conference> in <city>".
---

# Create a travel application (before the trip)

Shared tools live in the sibling skill folder `../travel-setup` (called `<travel-setup>`
below): scripts in `<travel-setup>/scripts`, rules in `<travel-setup>/references`.
Talk to the user in English unless they write German; values on the form stay German.
Never sign anything.

## 1. Profile
Run `python <travel-setup>/scripts/setup_profile.py show`. If there is no profile, do the setup
from `<travel-setup>/SKILL.md` first. For trips abroad the profile needs the pension/social
insurance number — ask if it is empty.

## 2. Collect the trip facts
Take what the user already said (and any invitation, acceptance mail, conference website or
booking they point to — read it) and ask **in one message** only for what is missing:
- event and purpose (conference, workshop, company visit; own talk/poster/discussant?)
- destination city, country, venue address (abroad: needed for the A1 part)
- dates and approximate start/end times of the travel
- means of transport (default public transport/train; car, taxi, flight need a reason)
- cost centre — the default one from the profile; project cost centres only if the trip belongs to the
  project (see `references/rules.md` §7); ask, don't guess
- rough total cost estimate (train + hotel + fee; offer to estimate it for them)
- free accommodation/meals, costs paid by others, private days before/after the trip (must be
  stated in the application)
Look up the venue address and dates on the event website instead of asking when you can.

## 3. Fill the form
Write `application.json` following the docstring of
`<travel-setup>/scripts/fill_application.py` and run it. Country "Deutschland" → domestic form,
otherwise the abroad form (with the A1 / Entsendung section). For conferences and workshops
abroad, "previously posted" stays `false`. Save as `Dienstreiseantrag_<Trip>.pdf` in the trip
folder the user names (suggest creating one per trip, e.g. `2027 EMAC Madrid`, where all
receipts will be collected later). Render page 1 to check it, fix and re-run if needed.
Mention private parts of the trip in the purpose text if any.

## 4. Trips abroad: A1 request e-mail
Draft the e-mail from `references/chair-procedure.md` (template there) with the trip and
profile data and show it to the user to send to the A1 contact at the travel department.
Do not insert names or e-mail addresses of staff; the user fills in the recipient.
Remind them that the abroad form has a Pflichtvorsorge section (page 3) they must check.

## 5. Next steps (always end with this)
Give a short numbered list, e.g.:
1. Check the application; sign it.
2. Hand it to the chair's secretary or the chair holder for approval (the dean's office signs
   too). Travel only after approval and keep the signed form.
3. Abroad: send the A1 e-mail now — the certificate must exist before the trip.
4. Book train/hotel with the university invoice address (see rules.md §7) and keep all
   invoices, tickets and payment proofs in the trip folder.
5. After the trip: run `/create-reimbursement <trip folder>` — deadline 6 months after return.

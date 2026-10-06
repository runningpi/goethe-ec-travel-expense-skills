# Travel expense skills — Chair of Electronic Commerce, Goethe University Frankfurt

[Claude skills](https://docs.claude.com/en/docs/agents-and-tools/agent-skills/overview) that do
the business-trip paperwork for members of the Chair of Electronic Commerce: travel
applications before a trip, the complete expense claim after it, and the BahnCard
reimbursement. Claude asks for anything that is missing instead of guessing, and tells you
your next steps when it is done.

## Skills

| Command | When | What you get |
|---|---|---|
| `/travel-setup` | once | Your profile (name, IBAN, address, cost centres, BahnCard, data for A1 requests), read from an old claim or application. |
| `/create-travel-application` | **before** a trip | Filled travel application (*Antrag auf Genehmigung einer Dienstreise*), domestic or abroad; for trips abroad also the draft e-mail requesting the A1 certificate. |
| `/create-reimbursement <trip folder>` | **after** a trip | One submission-ready PDF: filled *Reisekostenrechnung* (incl. annex) + approved application + A1 + every invoice with payment proof and ticket + programme with your talk marked. Bank statements are redacted, the folder is tidied up on request. |
| `/bahncard-reimbursement` | when your BahnCard has paid off | Finds all business tickets booked with your BahnCard, computes the savings, writes the request letter and attaches it to a claim. |

You can also just ask in your own words ("do the travel claim for my SALTY trip in
`D:\Trips\2026 SALTY`") — Claude picks the right skill.

## How to use it

1. **Setup:** `/travel-setup` and give Claude an old filled Reisekostenabrechnung or
   Dienstreiseantrag (PDF).
2. **Before a trip:** `/create-travel-application` — e.g. "EMAC 2027 in Madrid, 25–28 May, I
   present a paper". Create one folder per trip (e.g. `2027 EMAC Madrid`).
3. **During/after the trip:** drop *everything* into that folder — application, DB invoice and
   ticket (PDF or app screenshot), hotel invoice, conference invoice/receipt, payment proofs
   (bank statement export, banking-app or PayPal screenshots), programme if you have it.
   File names don't matter.
4. `/create-reimbursement "D:\Trips\2027 EMAC Madrid"` — answer Claude's questions (cost
   centre, meals received, your role, missing receipts), check the result, sign, and follow
   the next steps it gives you.

## Install

1. Download this repository (green *Code* button → *Download ZIP*, or `git clone`).
2. Copy the **four folders inside `skills/`** into your personal skills folder
   (they must stay next to each other — the other skills use the scripts in `travel-setup`):
   - Windows: `C:\Users\<you>\.claude\skills\`
   - macOS/Linux: `~/.claude/skills/`
3. Install Python 3 and run `pip install -r requirements.txt`.
4. Restart Claude Code / the Claude desktop app (Code tab) and type `/travel-setup`.

## Privacy

Your personal data is stored only on your computer in `~/.goethe-ec-travel-expenses/`.
Nothing personal is part of this repository, and `.gitignore` keeps PDFs, images and profiles
out of it. Official university forms are downloaded from the
[Formularcenter](https://www.uni-frankfurt.de/47065133/Formularcenter) when needed.
The skills never insert signatures — you sign yourself.

## Disclaimer

Unofficial helper of the chair, not a product of the university administration. The rules
summary follows the university's
[Merkblatt zum Hessischen Reisekostenrecht](https://www.uni-frankfurt.de/48628978/reisekosten_merkblatt.pdf);
the Reisekostenstelle has the final word. Check every document before you sign it.

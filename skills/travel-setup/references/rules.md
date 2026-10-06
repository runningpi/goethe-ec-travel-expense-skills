# Travel expense rules (Goethe University / Hessian travel law)

Condensed from the university's *Merkblatt zum Hessischen Reisekostenrecht*
(https://www.uni-frankfurt.de/48628978/reisekosten_merkblatt.pdf). When a case is not covered
here or looks unusual, read the original (`scripts/common.py` knows its URL as `guidelines`)
or tell the user to ask the Reisekostenstelle — do not guess on money questions.

## Contents
1. Approval and deadlines
2. What can be reimbursed (transport, hotel, fees, incidentals)
3. Per diem (Tagegeld) and meals
4. Trips abroad
5. Special cases (private extension, cancelled trips, refunds, third-party payments)
6. BahnCard
7. Chair conventions (Chair of Electronic Commerce)

## 1. Approval and deadlines
- Every business trip needs an approved application **before** it starts
  ("Antrag auf Genehmigung einer Dienstreise", domestic or abroad form). Without it: no
  reimbursement and no accident insurance. The signed application is attached to the claim.
- Changes to the plan (dates, private extension, car use) must be stated in the application.
- **Deadline: 6 months** after the day the trip ended (for a cancelled trip: after the day the
  cancellation became known). After that the claim is void. Warn the user if a trip is older
  than ~5 months.
- The claim must be signed by the traveller and signed "sachlich richtig" by the supervisor.

## 2. What can be reimbursed
**Public transport** (default means of transport): lowest class; 1st class only above 200 km
one way or with a valid reason. Reservations and IC/ICE surcharges are fine. If the trip starts
or ends at home, at most the cost from/to the workplace is paid. Use discounts (BahnCard,
Sparpreis). Within Hesse the Landesticket is free for employees — local tickets inside Hesse
are normally not reimbursed.

**Taxi / rental car / private car** only with a valid reason (heavy luggage, health, no public
transport at that time, ...). The reason goes on the form and, for taxis, on the annex page.
Without a valid reason: only the public-transport equivalent; private car 0,21 €/km (max.
130 €), with reason 0,35 €/km domestic / 0,30 €/km abroad.

**Hotel** (Übernachtungskosten): actual cost up to **80 € per night** domestic (abroad: country
rates, see section 4). Above 80 € → tick a reason on the annex page (Anlage) — e.g. conference
hotel / organiser's room contingent, trade fair, no cheaper option. Without receipts: flat
20 €/night domestic. Breakfast on the hotel bill: if the invoice is addressed to the university
(Dienstherr) the full bill incl. breakfast is paid and the per diem is cut; if addressed to the
person only, separately listed breakfast is not paid. Hotel invoices must be addressed to the
university and show net, VAT and gross. Double room shared with a non-traveller → only the
single-room price.

**Conference / participation fees** → "Teilnahmegebühr". **Incidentals** (Nebenkosten):
necessary costs such as booking fees, visa, business phone calls, entry fees. Not
reimbursable: tips, gifts, travel insurance (accident, health, cancellation), private
excursions.

**Receipts**: originals of everything; for amounts paid by card/PayPal the invoice plus a
payment proof. If a receipt is lost: a substitute receipt (Ersatzbeleg) with occasion, place,
date, item, amount, reason why the original is missing, signature, date.

## 3. Per diem (Tagegeld) and meals
- Domestic per calendar day of absence: < 8 h → 0 €; 8 – < 24 h → 14 €; 24 h → 28 €.
  Absence is measured from leaving home to returning home.
- Meals received for free (conference lunch, dinner, hotel breakfast paid by the university)
  are deducted from the per diem — they must be listed on page 2
  ("Verpflegungsanteile") and the radio "unentgeltliche Verpflegung" set to ja.
- Reduced after day 10 at the same place (domestic, −50 %) / day 14 abroad (−10 %).
- The traveller may waive the per diem ("Auszahlung Tagegeld: nein"), e.g. when everything
  was provided (chair retreat in Riezlern).

## 4. Trips abroad
- Use the abroad application form (contains the A1 / Entsendebescheinigung part). The
  university then requests the A1 certificate — attach it to the claim.
- Per diem and hotel limits follow the federal foreign rates (Auslandstage- und
  Übernachtungsgeld, PDF `foreign_rates`): e.g. Belgium 49 € per diem / hotel up to 141 €,
  Austria and others see the table. 80 % of the daily rate for days with 8–24 h.
- On the abroad application: "Ich war bereits in den letzten zwei Jahren ... eingesetzt" →
  **nein** for conference/workshop visits (a conference visit is not a posting).
- Foreign currency: attach the card statement showing the EUR amount.

## 5. Special cases
- **Private extension** (arriving earlier / staying longer for private reasons): reimburse
  only what the business trip alone would have cost. State the private part in the remarks;
  only claim the business nights; the private travel leg is not claimed if the user travelled
  privately. More than 5 private working days → mainly private trip (only extra costs).
- **Cancelled trip** (e.g. illness, strike): non-refundable costs (Sparpreis tickets,
  cancellation fees) are reimbursed; no per diem. Say so briefly in the remarks; the
  university usually already has the sick note — do not attach medical documents unless
  asked.
- **Refunds**: if a fee was refunded (look for "Erstattung"/credit bookings in the bank
  statement with the invoice number), do not claim it. Ask the user when unsure (a refund can
  also be a refund of a double payment).
- **Paid by someone else** (chair paid the hotel directly, organiser covered meals): do not
  claim it; tick "unentgeltliche Übernachtung/Verpflegung" accordingly.
- **Leisure costs** during a trip (cable car, e-bike rental, sightseeing) are not claimed.

## 6. BahnCard
A privately bought BahnCard can be reimbursed when the **savings on business trips during
its validity exceed its price**. Savings per ticket: price without BahnCard − price paid, with
BahnCard 50 = 50 % on Flexpreis/Normalpreis, 25 % on Sparpreis/Super Sparpreis; BahnCard 25 =
25 %. Only tickets booked with that card (ticket says "mit 1 BC50"/"BC25") and travelled within
its validity count; tickets of a cancelled trip that had to be paid count too. Needed: request
letter, trip overview table, BahnCard invoice, payment proof. It is claimed as "sonstiges"
on the claim of one trip (usually the one that pushes the savings above the price).

## 7. Chair conventions (Chair of Electronic Commerce)
- Cost centres come from the user's profile: the chair's default cost centre and possibly
  project cost centres. A project cost centre is used **only if the trip is related to that
  project** — always ask
  the user which cost centre applies; never infer it from the application alone (the approved
  application may still show the default cost centre).
- Applications and claims are checked and signed by the chair holder ("sachlich richtig") and
  additionally signed by the dean's office. The full procedure (A1 request, signatures, in-house
  mail) is in `chair-procedure.md`.
- Chair retreat / doctoral colloquium in Riezlern / Kleinwalsertal (Haus Bergkranz, Austria →
  abroad form + A1): accommodation and meals are paid directly by the chair → free lodging
  and free meals = ja, no hotel cost, per diem usually waived; claim only the travel
  (DB ticket, bus Oberstdorf ↔ Walserschanze).
- Book DB tickets and hotels with the invoice address "Goethe-Universität Frankfurt,
  Professur für Electronic Commerce, Theodor-W.-Adorno-Platz 1, 60323 Frankfurt,
  VAT ID DE114110511".

"""Fill the official 'Reisekostenrechnung' (3 pages incl. Anlage) from a trip JSON + the profile.

  python fill_reimbursement.py --trip trip.json --out 01_Reiko_Abrechnung_<Trip>.pdf

trip.json (all keys optional except destination/purpose/dates; amounts as numbers or "12,34"):
{
  "destination": "Bremen", "purpose": "EMAC Fall Conference 2026",
  "start": {"date": "16.09.2026", "time": "06:26"}, "end": {"date": "18.09.2026", "time": "22:14"},
  "business_start": {"date": "16.09.2026", "time": "12:30"}, "business_end": {"date": "18.09.2026", "time": "17:30"},
  "transport": "Bahn",
  "cost_center": "<cost centre>",                   # default: profile.default_cost_center
  "own_car": false, "free_meals": true, "free_lodging": false, "hotel_breakfast": true,
  "per_diem": true, "lodging_allowance": false,
  "advance": 0, "ticket_provided": 0,
  "taxi_reason": "",
  "costs": {"hotel": [178.30], "transport": [50.98, 4.00], "flight": [], "taxi": [], "car_km": [],
            "passengers": [], "fee": [275.00], "incidental": [], "other": [], "deduction": 0},
  "remarks": "...", "meals_received": "Frühstück (17.+18.09.), ...",
  "annex": {"hotel": ["conference_hotel", "other"], "hotel_other": "...", "taxi": [], "taxi_other": ""},
  "date": "06.10.2026"                              # date of the report, default today
}
Prints the total so it can be double-checked against the receipts.
"""
import argparse
import datetime
import json

from common import ensure_utf8_stdout, fill_form, get_form, load_profile, money, parse_money

COST_SLOTS = {
    "hotel": ["HotelÜbernachtungskosten", "HotelÜbernachtungskosten 2"],
    "transport": ["ÖPNVBahnkosten", "ÖPNVBahnkosten 2", "ÖPNVBahnkosten 3", "ÖPNVBahnkosten 4"],
    "flight": ["Flugkosten", "Flugkosten 2", "Flugkosten 3"],
    "taxi": ["Kosten für Taxi / Mietwagen", "Kosten für Taxi / Mietwagen 2"],
    "car_km": ["Kilometer bei Benutzung des eigenen PKWs", "Kilometer bei Benutzung des eigenen PKWs 2",
               "Kilometer bei Benutzung des eigenen PKWs 3"],
    "passengers": ["Mitfahrer namentlich inkl. mitgefahrenen Kilometeranzahl",
                   "Mitfahrer namentlich inkl. mitgefahrenen Kilometeranzahl 2",
                   "Mitfahrer namentlich inkl. mitgefahrenen Kilometeranzahl 3"],
    "fee": ["Teilnahmegebühr", "Teilnahmegebühr 2"],
    "incidental": ["Nebenkosten", "Nebenkosten 2", "Nebenkosten 3"],
    "other": ["sonstiges", "sonstiges 2"],
}
ANNEX_TAXI = {
    "main_transport_unreachable": "anders das Hauptverkehrsmittel nicht erreicht werden konnte",
    "venue_unreachable": "der Geschäftsort Tagungsort Fortbildungsort nicht anders bzw nicht pünktlich erreicht",
    "home_unreachable": "die Wohnung nach beendeter Dienstreise nicht mehr mit öffentlichen Verkehrsmitteln erreicht",
    "heavy_luggage": "umfangreiches bzw schweres AktenmaterialGepäck mitgeführt wurde",
    "health": "gesundheitliche Gründe bekannt nach Aktenlage dies erforderlich machten",
    "other": "Sonstige triftige Gründe bitte anführen",
}
ANNEX_HOTEL = {
    "conference_hotel": "es sich um das Tagungshotel handelte Die anderen Teilnehmer waren dort ebenfalls",
    "trade_fair_surcharge": "zeitgleich am Geschäftsort eine Messe stattfand und ein Messezuschlag auf den Zimmerpreis",
    "major_event": "zeitgleich am Geschäftsort eine Messe sportliche Großveranstaltung oder ähnliches stattfand",
    "late_registration": "die Anmeldung zur Teilnahme an der TagungVeranstaltung ohne eigenes Verschulden nur",
    "no_cheaper_option": "trotz nachhaltiger Bemühungen am Geschäftsort bzw in der näheren Umgebung Umkreis von",
    "other": "Sonstige Gründe bitte anführen",
}
# radio groups on page 1; option 0 = left box = "ja"
RADIOS = {
    "own_car": "Nutzung des eigenen KFZ",
    "free_meals": "unentgeltliche Verpflegung",
    "free_lodging": "unentgeltliche Übernachtung",
    "hotel_breakfast": "Frühstück im Hotel erhalten",
    "per_diem": "Auszahlung Tagegeld",
    "lodging_allowance": "Auszahlung Übernachtungsgeld",
}
RADIO_DEFAULTS = {"own_car": False, "free_meals": False, "free_lodging": False, "hotel_breakfast": False,
                  "per_diem": True, "lodging_allowance": False}


def hm(t):
    if not t:
        return "", ""
    h, m = t.replace(".", ":").split(":")
    return h.zfill(2), m.zfill(2)


def build_fields(trip, prof):
    t = {
        "Name, Vorname": prof["name"], "Telefonnummer": prof.get("phone", ""),
        "Institut / Abteilung": prof.get("institute", ""), "FB/Bereich": prof.get("department", ""),
        "Adresse": prof.get("address", ""), "Bankleitzahl": prof.get("iban", ""), "Kontonummer": "",
        "Bankinstitut": prof.get("bank", ""),
        "KostenstelleProjekt": trip.get("cost_center") or prof.get("default_cost_center", ""),
        "Reiseziel/Ort": trip["destination"], "Grund der Reise": trip["purpose"],
        "Verkehrsmittel": trip.get("transport", ""),
        "Abschlag": money(parse_money(trip.get("advance", 0))),
        "Fahrkarte": money(parse_money(trip.get("ticket_provided", 0))),
        "Falls TaxiMietwagen als Beförderungsmittel genutzt wurde bitte begründen": trip.get("taxi_reason", ""),
        "Datum": trip.get("date") or datetime.date.today().strftime("%d.%m.%Y"),
        "Bemerkungen": trip.get("remarks", ""),
        "Verpflegungsanteile Welche Verpflegung haben Sie während der Dienstreise kostenlos erhalten":
            trip.get("meals_received", ""),
        "Text2": prof.get("display_name") or prof["name"],
        "Text3": (trip.get("end") or {}).get("date", ""),
    }
    for key, (dfield, hfield, mfield) in {
        "start": ("Beginn der Reise Datum", "Beginn der Reise Uhrzeit Std", "Beginn der Reise Uhrzeit Min"),
        "end": ("Ende der Reise Datum", "Ende der Reise Uhrzeit Std", "Ende der Reise Uhrzeit Min"),
        "business_start": ("Beginn1. Dienstgeschäft", "Beginn 1. Dienstgeschäft Uhrzeit Std",
                           "Beginn 1. Dienstgeschäft Uhrzeit Min"),
        "business_end": ("Ende Dienstgeschäft", "Ende Dienstgeschäft Uhrzeit Std", "Ende Dienstgeschäft Uhrzeit Min"),
    }.items():
        v = trip.get(key) or {}
        t[dfield] = v.get("date", "")
        t[hfield], t[mfield] = hm(v.get("time", ""))

    total = 0.0
    costs = trip.get("costs", {})
    for cat, slots in COST_SLOTS.items():
        items = [parse_money(x) for x in costs.get(cat, [])]
        if len(items) > len(slots):
            raise SystemExit(f"Too many '{cat}' items ({len(items)}) for {len(slots)} slots on the form. "
                             f"Combine items of the same kind (e.g. both directions of one ticket).")
        for slot, amount in zip(slots, items):
            t[slot] = money(amount)
            total += amount
    deduction = parse_money(costs.get("deduction", 0) or 0)
    if deduction:
        t["Eigenanteil  Zuschuss Abzug"] = "-" + money(deduction)
        total -= deduction
    t["Gesamt"] = money(total)

    annex = trip.get("annex", {})
    if annex.get("hotel_other"):
        t["Text5"] = annex["hotel_other"]
    if annex.get("taxi_other"):
        t["Text4"] = annex["taxi_other"]
    checks = [ANNEX_HOTEL[k] for k in annex.get("hotel", [])] + [ANNEX_TAXI[k] for k in annex.get("taxi", [])]

    radios = {}
    for key, field in RADIOS.items():
        val = trip.get(key, RADIO_DEFAULTS[key])
        radios[(0, field)] = 0 if val else 1

    fontsizes = {}
    for f in ("Bemerkungen",
              "Verpflegungsanteile Welche Verpflegung haben Sie während der Dienstreise kostenlos erhalten"):
        n = len(t.get(f, ""))
        fontsizes[f] = 9 if n <= 160 else (8 if n <= 210 else 7)
    fontsizes["Text4"] = fontsizes["Text5"] = 7
    fontsizes["Text2"] = 0  # 0 = auto-fit; the name box on the annex page is narrow
    return t, checks, radios, fontsizes, total


def main():
    ensure_utf8_stdout()
    ap = argparse.ArgumentParser()
    ap.add_argument("--trip", required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    trip = json.load(open(a.trip, encoding="utf-8"))
    prof = load_profile()
    t, checks, radios, fontsizes, total = build_fields(trip, prof)
    t = {k: v for k, v in t.items() if v != ""}
    fill_form(get_form("reimbursement"), a.out, t, checks, radios, fontsizes)
    print(f"Wrote {a.out}  |  Gesamt = {money(total)} EUR")


if __name__ == "__main__":
    main()

"""Fill the official travel application ('Antrag auf Genehmigung einer Dienstreise').

  python fill_application.py --trip application.json --out 02_Dienstreiseantrag_<Trip>.pdf

The form (domestic vs. abroad) is chosen from `country`: "Deutschland" -> domestic form,
anything else -> form for trips abroad (incl. A1 / Entsendebescheinigung section).

application.json:
{
  "country": "Belgien", "destination": "Leuven", "purpose": "Konferenzteilnahme (SALTY 2026)",
  "start": {"date": "26.09.2026", "time": "14:00"}, "end": {"date": "29.09.2026", "time": "17:30"},
  "cost_center": "3502030005", "estimated_cost": "800",
  "transport": ["public", "train"],            # public, train, bus, flight, taxi, own_car, official_car, rental_car
  "car_reason": "", "taxi_reason": "",
  "free_lodging": false, "free_meals": false, "third_party_pays": false,
  "waive": [],                                   # per_diem, lodging, travel, incidental, all
  "teaching": "no_cancellation",                 # no_cancellation | substitute | make_up
  "substitute": "",
  "date": "30.07.2026",                          # date the applicant signs
  # abroad only:
  "abroad_address": {"street": "Hotelstraat 1", "city": "3000 Leuven, Belgien"},
  "workplace": {"name": "KU Leuven, Faculty of Economics and Business", "street": "Groot Begijnhof 14", "city": "3000 Leuven"},
  "activity": "Konferenzteilnahme",
  "previously_posted": false,                    # 'in den letzten zwei Jahren ... eingesetzt' -> conferences: false
  "travel_warning": false
}
The Pflichtvorsorge (occupational health) section of the abroad form is left for the
user/doctor; tell the user to check it.
"""
import argparse
import datetime
import json

from common import ensure_utf8_stdout, fill_form, get_form, load_profile

DOMESTIC = {
    "text": {
        "name": "Antragstellerin  Name Vorname", "department": "FachbereichInstitutAbteilung", "phone": "Telefon",
        "cost_center": "Die Reise wird aus ProjektKostenstelle bezahlt", "destination": "Dienstreiseort",
        "purpose": "Grund der Reise", "start_date": "Voraussichtliche Datum Beginn der Reise",
        "start_time": "Voraussichtliche Uhrzeit Beginn der Reise", "end_date": "Voraussichtliche Datum Ende der Reise",
        "end_time": "Voraussichtliche Uhrzeit Ende der Reise", "estimated_cost": "Kosten",
        "car_reason": "Grund für die Benutzung des eigenen KFZ oder Mietwagen es sind nur triftige Gründe zulässigRow1",
        "taxi_reason": "Grund für die Benutzung eines Taxis es sind nur triftige Gründe zulässigRow1",
        "substitute": "Vertretung", "date": "DatumRow1",
    },
    "transport": {"public": "Öff Verkehrsmittel", "train": "Bahn", "taxi": "Taxi", "official_car": "Dienstwagen",
                  "own_car": "eigenes KFZ", "flight": "Flug", "rental_car": "Mietwagen"},
    "flags": {"free_lodging": "Unentgeltliche Unterkunft", "free_meals": "Unentgeltliche Verpflegung",
              "third_party_pays": "Reisekosten werden von dritter Seite übernommen",
              "bahncard": "Ich besitze eine Bahncard"},
    "waive": {"per_diem": "Tagegeldes", "lodging": "Übernachtungsgeld", "travel": "Fahrtkosten",
              "incidental": "Nebenkosten", "all": "Reisekostenvergütung"},
    "teaching": {"substitute": "ist gesichert", "no_cancellation": "kein Ausfall",
                 "make_up": "die ausgefallenen Lehrveranstaltungen werden nachgeholt"},
}
ABROAD = {
    "text": {
        "name": "AntragsstellerIn Name, Vorname", "department": "Fachbereich/Institut/Abteilung", "phone": "Telefon",
        "cost_center": "Projekt/Kostenstelle", "destination": "Dienstreiseort", "country": "Dienstreiseland",
        "purpose": "Grund der Dienstreise", "start_date": "Datum Reisebeginn", "start_time": "Uhrzeit Reisebeginn",
        "end_date": "Datum Reiseende", "end_time": "Uhrzeit Reiseende", "ssn": "Sozialversicherungsnummer",
        "abroad_street": "Straße, Hausnummer Wohnadresse im ausländischen Beschäftigungsstaat",
        "abroad_city": "PLZ, Ort im ausländischen Beschäftigungsstaat",
        "workplace": "Einsatzstelle", "activity": "Art der Tätigkeit",
        "workplace_street": "Straße, Hausnummer Einsatzstelle", "workplace_city": "PLZ, Ort Einsatzstelle",
        "estimated_cost": "Kosten Reiko",
        "car_reason": "Triftiger Grund für die Benutzung des eigenen KFZ o. Mietwagen",
        "taxi_reason": "Triftiger Grund für die Benutzung eines Taxis",
        "substitute": "Name, Vorname Vertretung", "date": "Datum Genehmigung",
    },
    "transport": {"public": "Öffentliches Verkehrsmittel", "train": "Bahn", "bus": "Bus", "flight": "Flugzeug",
                  "taxi": "Taxi", "own_car": "eigenes Kraftfahrzeug", "official_car": "Dienstwagen",
                  "rental_car": "Mietwagen"},
    "flags": {"free_lodging": "Ich erhalte unentgeltlich Unterkunft",
              "free_meals": "Ich erhalte unentgeltlich Verpflegung",
              "third_party_pays": "Reisekosten werden von dritter Seite übernommen",
              "bahncard": "Ich besitze eine Bahncard"},
    "waive": {"per_diem": "Tagegeld", "lodging": "Übernachtungsgeld", "travel": "Fahrt-Flugkosten",
              "incidental": "Nebenkosten", "all": "Reisekostenvergütung"},
    "teaching": {"substitute": "durch eine Vertretung", "no_cancellation": "kein Lehr-Prüfungsausfall",
                 "make_up": "Nachholen ausgefallener Lehrveranstaltungen"},
    "no_fixed_workplace": "Ich habe im Ausland keine festen Beschäftigungsstellen während der Entsendung",
    # radio groups: (page index, field) -> labels from left to right
    "radios": {
        "health_insurance": ((0, "Krankenversicherung"), ["gesetzlich", "privat"]),
        "pension_fund": ((0, "Mitglied eines Versorgungswerks"), [False, True]),
        "extra_sheet": ((0, "Ergänzung Einsatzort"), [True, False]),  # printed as "ja | nein"
        "previously_posted": ((0, "war bereits im ausländischen Beschäftigungsstaaat eingesetzt Ja_nein"), [False, True]),
        "travel_warning": ((1, "Reisewarnung ja_nein"), [True, False]),
    },
}


def main():
    ensure_utf8_stdout()
    ap = argparse.ArgumentParser()
    ap.add_argument("--trip", required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    app = json.load(open(a.trip, encoding="utf-8"))
    prof = load_profile()
    abroad = app.get("country", "Deutschland").strip().lower() not in ("deutschland", "germany", "de")
    m = ABROAD if abroad else DOMESTIC

    vals = {
        "name": prof["name"], "department": prof.get("department_long", ""), "phone": prof.get("phone", ""),
        "cost_center": app.get("cost_center") or prof.get("default_cost_center", ""),
        "destination": app["destination"], "country": app.get("country", ""), "purpose": app["purpose"],
        "start_date": app["start"]["date"], "start_time": app["start"].get("time", ""),
        "end_date": app["end"]["date"], "end_time": app["end"].get("time", ""),
        "estimated_cost": str(app.get("estimated_cost", "")), "car_reason": app.get("car_reason", ""),
        "taxi_reason": app.get("taxi_reason", ""), "substitute": app.get("substitute", ""),
        "date": app.get("date") or datetime.date.today().strftime("%d.%m.%Y"),
        "ssn": prof.get("social_security_number", ""),
        "abroad_street": app.get("abroad_address", {}).get("street", ""),
        "abroad_city": app.get("abroad_address", {}).get("city", ""),
        "workplace": app.get("workplace", {}).get("name", ""), "activity": app.get("activity", ""),
        "workplace_street": app.get("workplace", {}).get("street", ""),
        "workplace_city": app.get("workplace", {}).get("city", ""),
    }
    text = {field: vals[k] for k, field in m["text"].items() if vals.get(k)}

    checks = [m["transport"][t] for t in app.get("transport", ["public", "train"])]
    if prof.get("bahncard", {}).get("type"):
        checks.append(m["flags"]["bahncard"])
    checks += [m["flags"][k] for k in ("free_lodging", "free_meals", "third_party_pays") if app.get(k)]
    checks += [m["waive"][k] for k in app.get("waive", [])]
    checks.append(m["teaching"][app.get("teaching", "no_cancellation")])

    radios = {}
    if abroad:
        checks.append(m["no_fixed_workplace"])
        choice = {
            "health_insurance": prof.get("health_insurance", "gesetzlich"),
            "pension_fund": bool(prof.get("pension_fund_member", False)),
            "extra_sheet": False,
            "previously_posted": bool(app.get("previously_posted", False)),
            "travel_warning": bool(app.get("travel_warning", False)),
        }
        for k, (key, labels) in m["radios"].items():
            radios[key] = labels.index(choice[k])
        if not vals["ssn"]:
            print("WARNING: social security number missing in profile (needed for the A1 certificate).")

    form = get_form("application_abroad" if abroad else "application_domestic")
    fill_form(form, a.out, text, checks, radios, {m["text"]["purpose"]: 0})
    print(f"Wrote {a.out} ({'abroad' if abroad else 'domestic'} form)")
    if abroad:
        print("Reminder: the Pflichtvorsorge section (page 3) is not filled - the user has to check it.")


if __name__ == "__main__":
    main()

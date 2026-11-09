from datetime import date, timedelta
import os
from urllib.request import Request, urlopen

# Almflair - Airbnb-iCal-Diagnose
# Nur Lesezugriff. Keine Dateien werden veraendert.

START = date(2027, 10, 20)
ENDE = date(2027, 12, 1)  # exklusiv


def lese_kalender():
    url = os.environ.get("AIRBNB_ICAL_URL", "")
    if not url.startswith("https://"):
        raise ValueError("Airbnb-Kalenderadresse fehlt oder ist ungueltig.")
    anfrage = Request(url, headers={"User-Agent": "Almflair-iCal-Diagnose/1.0"})
    with urlopen(anfrage, timeout=30) as antwort:
        daten = antwort.read(5_000_001)
    if len(daten) > 5_000_000:
        raise ValueError("Kalenderdatei ist zu gross.")
    inhalt = daten.decode("utf-8-sig")
    if "BEGIN:VCALENDAR" not in inhalt:
        raise ValueError("Keine gueltige Kalenderantwort.")
    return inhalt


def ereignisse_lesen(inhalt):
    zeilen = []
    for zeile in inhalt.replace("\r\n", "\n").split("\n"):
        if zeile.startswith((" ", "\t")) and zeilen:
            zeilen[-1] += zeile[1:]
        else:
            zeilen.append(zeile)

    ereignisse = []
    ereignis = None
    wiederholungen = 0
    for zeile in zeilen:
        if zeile == "BEGIN:VEVENT":
            ereignis = {}
        elif zeile == "END:VEVENT" and ereignis is not None:
            if "RRULE" in ereignis:
                wiederholungen += 1
            if "DTSTART" in ereignis and "DTEND" in ereignis:
                if ereignis.get("TRANSP", "").upper() != "TRANSPARENT":
                    ereignisse.append(ereignis)
            ereignis = None
        elif ereignis is not None and ":" in zeile:
            schluessel, wert = zeile.split(":", 1)
            ereignis[schluessel.split(";", 1)[0].upper()] = wert
    return ereignisse, wiederholungen


def datum_lesen(wert):
    return date.fromisoformat(
        wert[:4] + "-" + wert[4:6] + "-" + wert[6:8]
    )


def diagnose(ereignisse, wiederholungen):
    belegt = set()
    beruecksichtigt = 0

    for ereignis in ereignisse:
        try:
            beginn = datum_lesen(ereignis["DTSTART"])
            ende = datum_lesen(ereignis["DTEND"])
        except (ValueError, KeyError):
            continue

        if beginn >= ENDE or ende <= START or ende <= beginn:
            continue

        beruecksichtigt += 1
        tag = max(beginn, START)
        while tag < min(ende, ENDE):
            belegt.add(tag)
            tag += timedelta(days=1)

    print("ALMFLAIR - AIRBNB-ICAL-DIAGNOSE")
    print("Pruefzeitraum: 20.10.2027 bis 30.11.2027")
    print("Ereignisse insgesamt:", len(ereignisse))
    print("Ereignisse im Pruefzeitraum:", beruecksichtigt)
    print("Wiederkehrende Ereignisse:", wiederholungen)
    print()
    print("Datum       iCal-Status")

    tag = START
    while tag < ENDE:
        status = "BELEGT" if tag in belegt else "KEIN SPERREREIGNIS"
        print(tag.strftime("%d.%m.%Y"), status)
        tag += timedelta(days=1)

    print()
    print("Hinweis: KEIN SPERREREIGNIS bedeutet nicht")
    print("automatisch, dass der Tag online buchbar ist.")
    print("Wiederkehrende Ereignisse werden nicht expandiert.")
    print("Keine Aenderungen an Kalendern vorgenommen.")


if __name__ == "__main__":
    kalender = lese_kalender()
    daten, wiederholungen = ereignisse_lesen(kalender)
    diagnose(daten, wiederholungen)

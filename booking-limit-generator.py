# Almflair - Automatische Buchungsgrenze
# TESTVERSION - keine produktiven Kalender veraendern

import os
from datetime import datetime, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

# Grundeinstellungen
STANDARD_FRIST = 365
MAXIMALE_FRIST = 1095
VORSCHAU_ENDE_TAGE = 1460

# Testdatei - nicht mit Portalen verbunden
DATEINAME = "booking-limit-vorschau.ics"


def buchungsfrist_lesen():
    wert = os.environ.get(
        "BUCHUNGSFRIST_TAGE", str(STANDARD_FRIST)
    )
    tage = int(wert)

    if not 1 <= tage <= MAXIMALE_FRIST:
        raise ValueError(
            "Buchungsfrist muss zwischen 1 und "
            "1095 Tagen liegen."
        )
    return tage


def kalender_erzeugen():
    heute = datetime.now(
        ZoneInfo("Europe/Vienna")
    ).date()

    frist = buchungsfrist_lesen()
    grenze = heute + timedelta(days=frist)

    # Am Grenztag darf noch abgereist werden.
    # Die erste gesperrte Nacht beginnt am Grenztag.
    sperre_ab = grenze

    # Testhorizont: 1460 Tage ab heute
    sperre_bis = heute + timedelta(
        days=VORSCHAU_ENDE_TAGE
    )

    if sperre_ab >= sperre_bis:
        raise ValueError(
            "Die Sperrgrenze liegt ausserhalb "
            "des Testhorizonts."
        )

    zeitstempel = datetime.now(
        ZoneInfo("UTC")
    ).strftime("%Y%m%dT%H%M%SZ")

    zeilen = [
        "BEGIN:VCALENDAR",
        "VERSION:2.0",
        "PRODID:-//Almflair//Buchungsgrenze Test//DE",
        "CALSCALE:GREGORIAN",
        "METHOD:PUBLISH",
        "X-WR-CALNAME:Almflair Buchungsgrenze Test",
        "BEGIN:VEVENT",
        "UID:almflair-buchungsgrenze-test@github",
        f"DTSTAMP:{zeitstempel}",
        f"DTSTART;VALUE=DATE:{sperre_ab:%Y%m%d}",
        f"DTEND;VALUE=DATE:{sperre_bis:%Y%m%d}",
        "SUMMARY:Almflair Buchungsgrenze Test",
        "STATUS:CONFIRMED",
        "TRANSP:OPAQUE",
        "END:VEVENT",
        "END:VCALENDAR",
    ]

    inhalt = "\r\n".join(zeilen) + "\r\n"

    Path(DATEINAME).write_bytes(
        inhalt.encode("utf-8")
    )

    print("ALMFLAIR - BUCHUNGSGRENZE TEST")
    print("Heute:", heute.strftime("%d.%m.%Y"))
    print("Buchungsfrist:", frist, "Tage")
    print(
       "Letzter erlaubter Abreisetag:",
        grenze.strftime("%d.%m.%Y")
    )
    print(
        "Sperre ab:",
        sperre_ab.strftime("%d.%m.%Y")
    )
    print(
        "Test-Sperre bis (exklusiv):",
        sperre_bis.strftime("%d.%m.%Y")
    )
    print("Testdatei:", DATEINAME)
    print("Keine produktiven Kalender veraendert.")


if __name__ == "__main__":
    kalender_erzeugen()

import json
import os
from datetime import datetime, timedelta, timezone
from pathlib import Path
from zoneinfo import ZoneInfo

# Almflair - automatisch mitlaufende Buchungsgrenze
# Standard: 365 Tage, dauerhaft variabel einstellbar

KONFIGURATION = Path("booking-limit-config.json")

TESTDATEI = "booking-limit-vorschau.ics"
AUTODATEI = "booking-limit-auto.ics"

MAXIMALE_FRIST = 1095
SPERRHORIZONT_TAGE = 1460


def buchungsfrist_lesen():
    daten = json.loads(
        KONFIGURATION.read_text(encoding="utf-8")
    )

    tage = daten.get("buchungsfrist_tage")

    if type(tage) is not int or not 1 <= tage <= MAXIMALE_FRIST:
        raise ValueError(
            "Buchungsfrist muss eine ganze Zahl "
            "zwischen 1 und 1095 sein."
        )

    return tage


def ausgabedatei_lesen():
    name = os.environ.get(
        "BUCHUNGSGRENZE_DATEI", TESTDATEI
    )

    if name not in (TESTDATEI, AUTODATEI):
        raise ValueError("Unzulaessiger Dateiname.")

    return Path(name)


def kalender_erzeugen():
    heute = datetime.now(
        ZoneInfo("Europe/Vienna")
    ).date()

    frist = buchungsfrist_lesen()

    grenze = heute + timedelta(days=frist)

    # Abreise am Grenztag bleibt erlaubt.
    # Erste gesperrte Nacht beginnt am Grenztag.
    sperre_ab = grenze

    # Sperrhorizont: vier Jahre ab heute
    sperre_bis = heute + timedelta(
        days=SPERRHORIZONT_TAGE
    )

    if sperre_ab >= sperre_bis:
        raise ValueError(
            "Sperrgrenze liegt ausserhalb des Horizonts."
        )

    datei = ausgabedatei_lesen()

    zeitstempel = datetime.now(
        timezone.utc
    ).strftime("%Y%m%dT%H%M%SZ")

    zeilen = [
        "BEGIN:VCALENDAR",
        "VERSION:2.0",
        "PRODID:-//Almflair//Buchungsgrenze//DE",
        "CALSCALE:GREGORIAN",
        "METHOD:PUBLISH",
        "X-WR-CALNAME:Almflair Buchungsgrenze",
        "BEGIN:VEVENT",
        "UID:almflair-buchungsgrenze@github",
        f"DTSTAMP:{zeitstempel}",
        f"DTSTART;VALUE=DATE:{sperre_ab:%Y%m%d}",
        f"DTEND;VALUE=DATE:{sperre_bis:%Y%m%d}",
        "SUMMARY:Almflair Buchungsgrenze",
        "STATUS:CONFIRMED",
        "TRANSP:OPAQUE",
        "END:VEVENT",
        "END:VCALENDAR",
    ]

    inhalt = "\r\n".join(zeilen) + "\r\n"

    datei.write_bytes(inhalt.encode("utf-8"))

    # Technische Kontrolle der erzeugten Datei
    pruefung = datei.read_bytes()

    assert pruefung == inhalt.encode("utf-8")
    assert inhalt.count("BEGIN:VEVENT") == 1
    assert inhalt.count("END:VEVENT") == 1
    assert sperre_ab < sperre_bis

    print("ALMFLAIR - BUCHUNGSGRENZE")
    print("Heute:", heute.strftime("%d.%m.%Y"))
    print("Vorausbuchungsfrist:", frist, "Tage")
    print(
        "Letzter erlaubter Abreisetag:",
        grenze.strftime("%d.%m.%Y")
    )
    print(
        "Erste gesperrte Nacht:",
        sperre_ab.strftime("%d.%m.%Y")
    )
    print(
        "Sperrende (exklusiv):",
        sperre_bis.strftime("%d.%m.%Y")
    )
    print("Erzeugte Datei:", datei)
    print("Validierung: erfolgreich")
    print("Keine Portal-Kalender veraendert.")


if __name__ == "__main__":
    kalender_erzeugen()

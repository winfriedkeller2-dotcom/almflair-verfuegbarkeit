import json
from datetime import datetime, timedelta, timezone
from pathlib import Path
from zoneinfo import ZoneInfo

# Almflair - variable Buchungsgrenze
# TESTBETRIEB: Keine produktiven Kalender veraendern.

KONFIGURATION = Path("booking-limit-config.json")
TESTDATEI = Path("booking-limit-vorschau.ics")

STANDARD_FRIST = 365
MAXIMALE_FRIST = 1095
TESTHORIZONT_TAGE = 1460


def buchungsfrist_lesen():
    if not KONFIGURATION.is_file():
        raise FileNotFoundError(
            "Konfigurationsdatei fehlt: " + str(KONFIGURATION)
        )

    daten = json.loads(KONFIGURATION.read_text(encoding="utf-8"))
    tage = daten.get("buchungsfrist_tage")

    if type(tage) is not int or not 1 <= tage <= MAXIMALE_FRIST:
        raise ValueError(
            "buchungsfrist_tage muss eine ganze Zahl "
            "zwischen 1 und 1095 sein."
        )

    return tage


def kalender_erzeugen():
    heute = datetime.now(ZoneInfo("Europe/Vienna")).date()
    frist = buchungsfrist_lesen()

    grenze = heute + timedelta(days=frist)
    sperre_ab = grenze
    sperre_bis = heute + timedelta(days=TESTHORIZONT_TAGE)

    if sperre_ab >= sperre_bis:
        raise ValueError("Sperrgrenze ausserhalb des Testhorizonts.")

    zeitstempel = datetime.now(timezone.utc).strftime(
        "%Y%m%dT%H%M%SZ"
    )

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

    TESTDATEI.write_bytes(
        ("\r\n".join(zeilen) + "\r\n").encode("utf-8")
    )

    print("ALMFLAIR - AUTOMATISCHE BUCHUNGSGRENZE (TEST)")
    print("Heute:", heute.strftime("%d.%m.%Y"))
    print("Konfiguration:", KONFIGURATION)
    print("Vorausbuchungsfrist:", frist, "Tage")
    print("Letzter erlaubter Abreisetag:",
          grenze.strftime("%d.%m.%Y"))
    print("Sperrbeginn:",
          sperre_ab.strftime("%d.%m.%Y"))
    print("Sperrende (exklusiv):",
          sperre_bis.strftime("%d.%m.%Y"))
    print("Erzeugte Testdatei:", TESTDATEI)
    print("Keine produktiven Kalender veraendert.")


if __name__ == "__main__":
    kalender_erzeugen()

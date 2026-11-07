# Almflair - Vorschau der variablen Vorausbuchungsfrist
# Reiner Testbetrieb: keine Kalenderdateien werden veraendert.

from datetime import date, timedelta

# EINSTELLUNG: Maximale Vorausbuchungsfrist in Tagen
BUCHUNGSFRIST_TAGE = int(__import__("os").environ.get("BUCHUNGSFRIST_TAGE", "365"))

def berechne_buchungsgrenze(heute, tage):
    if tage < 1:
        raise ValueError("Die Buchungsfrist muss mindestens 1 Tag betragen.")
    return heute + timedelta(days=tage)


def pruefe_anreise(anreise, grenze):
    return anreise <= grenze


def main():
    heute = date.today()
    grenze = berechne_buchungsgrenze(heute, BUCHUNGSFRIST_TAGE)

    print("ALMFLAIR - BUCHUNGSGRENZE (TEST)")
    print("Heute:", heute.strftime("%d.%m.%Y"))
    print("Vorausbuchungsfrist:", BUCHUNGSFRIST_TAGE, "Tage")
    print("Letzter erlaubter Anreisetag:", grenze.strftime("%d.%m.%Y"))
    print()
    print("Testfaelle:")

    testdaten = [
        grenze - timedelta(days=1),
        grenze,
        grenze + timedelta(days=1),
        date(2028, 2, 4),
    ]

    for anreise in testdaten:
        status = "Innerhalb der Frist" if pruefe_anreise(anreise, grenze) else "Ausserhalb der Frist"
        print(anreise.strftime("%d.%m.%Y"), "-", status)

    print()
    print("Nur Vorschau - keine Aenderungen an Buchungskalendern.")


if __name__ == "__main__":
    main()

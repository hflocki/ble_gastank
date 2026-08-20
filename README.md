# ble_gastank – Kompatibel mit BLE-Gastanksensoren wie SRG WAVE / DIMES

Eine passive Home Assistant Custom Component zum Auslesen von Bluetooth-Gastanksensoren über Home Assistant Bluetooth oder ESP32 Bluetooth Proxies.

![hacs_badge](https://img.shields.io/badge/HACS-Custom-41BDF5.svg)
![AI Generated](https://img.shields.io/badge/README-AI%20Generated-7A00FF.svg)

## Features

* **100 % Passiv & Batterieschonend:** Hört rein passiv auf die BLE-Advertisements. Keinerlei aktive Verbindungen nötig – schont die Batterie des Sensors und verhindert Verbindungsabbrüche.
* **Füllstopp-Korrektur:** Berücksichtigt mechanische Füllstopps (z. B. 80 %). Ist der Tank am Füllstopp voll geklickt, zeigt die Integration **100 % nutzbare Füllung** an.
* **Exakte Liter-Berechnung:** Berechnet den reellen Gasinhalt in Litern basierend auf dem eingestellten Brutto-Flaschenvolumen (z. B. 22 Liter Tankflasche).
* **Nachträglich anpassbar (Options Flow):** Flaschenvolumen und Füllstopp können jederzeit über die Einstellungen in Home Assistant geändert werden.
* **Bequeme UI-Konfiguration:** Vollständige Einrichtung direkt über die Home Assistant Benutzeroberfläche.

---

## Erstellte Sensoren

Nach der Einrichtung legt die Integration ein Gerät **Gastank BLE** mit 3 Entitäten an:

* 🔋 **Batterie** (`%`)
* 📊 **Füllstand** (`%` – skaliert auf die nutzbare Kapazität bezogen auf den Füllstopp)
* ⛽ **Füllstand Liter** (`L` – berechneter Inhalt in Litern)

---

## Installation über HACS

1. Öffne **HACS** in Home Assistant.
2. Klicke oben rechts auf die **drei Punkte (⋮)** → **Benutzerdefinierte Repositories** (*Custom Repositories*).
3. Füge die Repository-URL ein: `https://github.com/hflocki/ble_gastank`
4. Wähle als Kategorie **Integration** aus und klicke auf **Hinzufügen**.
5. Suche nach **BLE Gastank**, klicke auf **Herunterladen** und starte Home Assistant neu.

---

## Konfiguration

1. Gehe in Home Assistant zu **Einstellungen** → **Geräte & Dienste** → **Integration hinzufügen**.
2. Suche nach **BLE Gastank**.
3. Trage deine Werte im Formular ein:
   * **MAC-Adresse:** Bluetooth-Adresse deines Sensors (z. B. `AA:BB:CC:11:22:33`)
   * **Flaschenvolumen:** Gesamtes Brutto-Volumen der Flasche in Litern (z. B. `22.0`)
   * **Füllstopp:** Abschaltschwelle des Füllstopps in % (Standard: `80` %).  
     > 💡 **Hinweis:** Wenn deine Gasflasche keinen mechanischen Füllstopp besitzt, trage hier einfach **`100`** ein.

---

### Disclaimer / Haftungsausschluss

Dieses Projekt steht in keinerlei Verbindung zur Rotarex S.A. oder deren eingetragenen Marken (wie DIMES oder SRG WAVE). Es handelt sich um ein inoffizielles Community-Projekt zur rein passiven Datenverarbeitung für Home Assistant.

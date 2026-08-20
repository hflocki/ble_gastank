# ble_gastank 
– Kompatibel mit BLE-Gastanksensoren wie SRG WAVE / DIMES

Eine passive Home Assistant Custom Component zum Auslesen von **Bluetooth-Gastanksensoren** über Home Assistant Bluetooth oder ESP32 Bluetooth Proxies.

![hacs_badge](https://img.shields.io/badge/HACS-Custom-41BDF5.svg)
![AI Generated](https://img.shields.io/badge/README-AI%20Generated-7A00FF.svg)

## Features

* **100 % Passiv & Batterieschonend:** Hört rein passiv auf die BLE-Advertisements. Keinerlei aktive Verbindungen nötig – schont die Batterie des Sensors und verhindert Verbindungsabbrüche.
* **Füllstopp-Korrektur:** Berücksichtigt den mechanischen Füllstopp (z. B. 80 %) und rechnet den Sensor-Rohwert auf den tatsächlichen Füllstand der Flasche um.
* **Exakte Liter-Berechnung:** Berechnet den reellen Gasinhalt in Litern basierend auf dem eingestellten Flaschenvolumen (z. B. 22 Liter Tankflasche).
* **Bequeme UI-Konfiguration:** Vollständige Einrichtung direkt über die Home Assistant Benutzeroberfläche (Config Flow).

---

## Erstellte Sensoren

Nach der Einrichtung legt die Integration ein Gerät **Gas Tank** mit 3 Entitäten an:

* 🔋 **Batterie** (`%`)
* 📊 **Füllstand** (`%` – skaliert auf den echten Füllstand unter Berücksichtigung des Füllstopps)
* ⛽ **Füllstand Liter** (`L` – berechneter Inhalt in Litern)

---

## Installation über HACS

1. Öffne **HACS** in Home Assistant.
2. Klicke oben rechts auf die **drei Punkte (⋮)** → **Benutzerdefinierte Repositories** (*Custom Repositories*).
3. Füge die Repository-URL ein: `https://github.com/hflocki/ble_gastank`
4. Wähle als Kategorie **Integration** aus und klicke auf **Hinzufügen**.
5. Suche nach **ble_gastank**, klicke auf **Herunterladen** und starte Home Assistant neu.

---

## Konfiguration

1. Gehe in Home Assistant zu **Einstellungen** → **Geräte & Dienste** → **Integration hinzufügen**.
2. Suche nach **ble_gastank**.
3. Trage deine Werte im Formular ein:
   * **MAC-Adresse:** Bluetooth-Adresse deines Dimes-Sensors (z. B. `00:00:00:00:00:00`)
   * **Flaschenvolumen:** Gesamtes Brutto-Volumen der Flasche in Litern (z. B. `22.0`)
   * **Füllstopp:** Abschaltschwelle des Füllstopps in % (z. B. `80`)

---

### Disclaimer / Haftungsausschluss

Dieses Projekt steht in keinerlei Verbindung zur Rotarex S.A. oder deren eingetragenen Marken (wie DIMES oder SRG WAVE). Es handelt sich um ein inoffizielles Community-Projekt zur rein passiven Datenverarbeitung für Home Assistant.

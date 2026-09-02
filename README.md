# ble_gastank 

<img src="/logo/icon.png" alt="BLE_Gastank Logo" width="150">

Kompatibel mit BLE-Gastanksensoren wie SRG WAVE / DIMES und Truma LevelControl

Eine Home Assistant Custom Component zum Auslesen von Bluetooth-Gastanksensoren über Home Assistant Bluetooth oder ESP32 Bluetooth Proxies.

![hacs_badge](https://img.shields.io/badge/HACS-Custom-41BDF5.svg)
![AI Generated](https://img.shields.io/badge/README-AI%20Generated-7A00FF.svg)

## Features

* **Unterstützung verschiedener Sensoren:** Wähle während der Einrichtung direkt zwischen DIMES (Rotarex/SRG Wave) und Truma LevelControl.
* **100 % Passiv & Batterieschonend (DIMES):** Hört rein passiv auf die BLE-Advertisements. Keinerlei aktive Verbindungen nötig.
* **Aktiver GATT-Abruf (Truma LevelControl):** Liest die Daten des Truma LevelControl im einstellbaren Intervall direkt per BLE aus.
* **Füllstopp-Korrektur:** Berücksichtigt mechanische Füllstopps (z. B. 80 %). Ist der Tank am Füllstopp voll geklickt, zeigt die Integration **100 % nutzbare Füllung** an.
* **Exakte Liter-Berechnung:** Berechnet den reellen Gasinhalt in Litern basierend auf dem eingestellten Brutto-Flaschenvolumen (z. B. 22 Liter Tankflasche).
* **Nachträglich anpassbar (Options Flow):** Sensortyp, Flaschenvolumen und Füllstopp können jederzeit über die Einstellungen in Home Assistant geändert werden.
* **Bequeme UI-Konfiguration:** Vollständige Einrichtung direkt über die Home Assistant Benutzeroberfläche.
* **Rohwert-Sensor:** Stellt zusätzlich den unkorrigierten 1:1 Sensorwert zur Verfügung.

---

## Erstellte Sensoren

Nach der Einrichtung legt die Integration ein Gerät **Gastank BLE** an mit 4 Entitäten:

* Batterie (%)
* Füllstand Rohwert (% – unkorrigierter 1:1 Wert des Sensors)
* Füllstand (% – skaliert auf die nutzbare Kapazität bezogen auf den Füllstopp)
* Füllstand Liter (L – berechneter Inhalt in Litern)

---

## Installation über HACS

[![Open your Home Assistant instance and open a repository inside the Home Assistant Community Store.](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=hflocki&repository=https%3A%2F%2Fgithub.com%2Fhflocki%2Fble_gastank&category=Bluetooth)

oder

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
   * **Sensortyp:** Wähle zwischen *DIMES BLE Sensor* oder *Truma LevelControl*
   * **Flaschenvolumen:** Gesamtes Brutto-Volumen der Flasche in Litern (z. B. `22.0`)
   * **Füllstopp:** Abschaltschwelle des Füllstopps in % (Standard: `80` %).  
     > 💡 **Hinweis:** Wenn deine Gasflasche keinen mechanischen Füllstopp besitzt, trage hier einfach **`100`** ein.

---

### Disclaimer / Haftungsausschluss

Dieses Projekt steht in keinerlei Verbindung zur Rotarex S.A., Truma Gerätetechnik GmbH & Co. KG oder deren eingetragenen Marken (wie DIMES, SRG WAVE oder Truma LevelControl). Es handelt sich um ein inoffizielles Community-Projekt zur Datenverarbeitung für Home Assistant.

---

<a href="https://www.buymeacoffee.com/hflocki" target="_blank">
  <img src="https://cdn.buymeacoffee.com/buttons/v2/default-yellow.png" alt="Buy Me a Coffee" height="60" width="217">
</a>

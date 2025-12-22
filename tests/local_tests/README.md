# Lokales Testen mit einem echten Braiins OS Miner

Dieses Verzeichnis enthält Test-Skripte für manuelle Tests mit echter Hardware (Braiins OS Miner).

## 📋 Dateien

- **test_braiins_serials.py** - Test-Skript für Braiins Serial Number Feature
- **README.md** - Diese Dokumentation

## 🚀 Schnellanleitung

### Mit Standard-Zugangsdaten (root/root)

```bash
cd /workspaces/pyasic
python tests/local_tests/test_braiins_serials.py 192.168.1.100
```

### Mit benutzerdefinierten Zugangsdaten

```bash
python tests/local_tests/test_braiins_serials.py 192.168.1.100 admin meinpasswort
```

## ✅ Was wird getestet

Das Skript `test_braiins_serials.py` prüft:

1. **Miner-Verbindung**: Automatische Typ-Erkennung
2. **Miner Serial Number** (`get_serial_number()`)
   - Ruft die Seriennummer des Miners ab
   - Verfügbar ab Firmware 25.03

3. **PSU Serial Number** (`get_psu_serial_number()`)
   - Ruft die Seriennummer des Power Supply Units ab
   - Verfügbar ab Firmware 25.03

4. **Hashboard Serial Numbers**
   - Seriennummern aller Hashboards
   - Details pro Hashboard (Slot, Chips, Temperatur)

5. **Zusatzdaten**
   - IP, MAC Address
   - Firmware Version, API Version

## 📋 Voraussetzungen

- Python 3.8+
- Braiins OS Plus Miner mit Firmware 25.03 oder neuer (für Serial Number Support)
- Netzwerkzugriff zum Miner
- Miner-IP-Adresse und Zugangsdaten (Standard: root/root)

## 💡 Hinweise

- **Für ältere Firmware**: Wenn dein Miner Firmware < 25.03 hat, werden Serial Numbers nicht verfügbar sein
- **Standard-Zugangsdaten**: Die meisten Braiins OS Miner verwenden root/root als Standard
- **Netzwerk**: Der Miner muss über SSH (Port 22) und gRPC (Port 50051) erreichbar sein
- **Timeout**: Die Anfrage kann bis zu 30 Sekunden dauern, je nach Miner-Auslastung

## 🔧 Debuggen bei Fehlern

Falls das Skript Fehler meldet:

1. **Verbindungsfehler**: Überprüfe die IP-Adresse und Netzwerkverbindung
2. **Authentifizierung fehlgeschlagen**: Überprüfe Username und Passwort
3. **Firmware zu alt**: Überprüfe die Firmware-Version auf dem Miner (Mindestens 25.03)
4. **Service nicht erreichbar**: Überprüfe, ob der Miner online und erreichbar ist

## 📚 Weitere Informationen

Die neuen Features sind implementiert in:

- `pyasic/miners/backends/braiins_os.py` (BOSer-Backend)
- `pyasic/miners/base.py` (Basis-Interface)
- `pyasic/data/__init__.py` (Datenmodell)

Siehe GitHub PR #402 für vollständige Details.

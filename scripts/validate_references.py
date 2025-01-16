import os
import json

# Pfade zu den Ordnern
DATA_FOLDER = r"C:\Projekte\KNIME_Aufgabe\data"
REFERENCES_FOLDER = r"C:\Projekte\KNIME_Aufgabe\references"
MISSING_REFERENCES_FILE = os.path.join(REFERENCES_FOLDER, "missing_references.txt")

# Funktion zum Laden der Referenzstationen
def load_reference_stations(file_path):
    try:
        with open(file_path, 'r') as f:
            data = json.load(f)
            return {station["station_id"] for station in data.get("data", {}).get("stations", [])}
    except Exception as e:
        print(f"Fehler beim Laden der Referenzdatei {file_path}: {e}")
        return set()

# Funktion zur Überprüfung der station_id-Referenzen
def validate_station_ids(data_folder, reference_stations):
    errors = []
    missing_station_ids = set()

    for filename in os.listdir(data_folder):
        if filename.endswith(".json"):
            file_path = os.path.join(data_folder, filename)
            try:
                with open(file_path, 'r') as f:
                    data = json.load(f)
                    stations = data.get("data", {}).get("stations", [])

                    for station in stations:
                        station_id = station.get("station_id")
                        if station_id not in reference_stations:
                            errors.append((filename, station_id, "Ungültige station_id"))
                            if station_id:
                                missing_station_ids.add(station_id)

            except json.JSONDecodeError as e:
                errors.append((filename, None, f"Ungültiges JSON-Format: {e.msg}"))
            except Exception as e:
                errors.append((filename, None, f"Unerwarteter Fehler: {e}"))

    return errors, missing_station_ids

# Funktion zum Speichern der Fehler in einer Datei
def save_errors_to_file(errors, missing_station_ids, file_path):
    try:
        with open(file_path, 'w') as f:
            # Kopfzeile mit allen fehlenden Stationen
            f.write("Fehlende Stationen:\n")
            for station_id in sorted(missing_station_ids):
                f.write(f"- {station_id}\n")
            f.write("\nDetailierte Fehler:\n")

            # Detailierte Fehler
            for filename, station_id, error in errors:
                f.write(f"Datei: {filename}, Station: {station_id}, Fehler: {error}\n")
        print(f"Fehler wurden in {file_path} gespeichert.")
    except Exception as e:
        print(f"Fehler beim Schreiben der Datei {file_path}: {e}")

# Hauptfunktion
def main():
    # Lade Referenzstationen
    reference_file = os.path.join(REFERENCES_FOLDER, "station_information.json")
    reference_stations = load_reference_stations(reference_file)

    if not reference_stations:
        print("Keine Referenzstationen gefunden. Überprüfung wird abgebrochen.")
        return

    print(f"Referenzstationen geladen: {len(reference_stations)} Stationen")

    # Überprüfe station_id-Beziehungen
    errors, missing_station_ids = validate_station_ids(DATA_FOLDER, reference_stations)

    if errors:
        print("\nFehler in station_id-Referenzen gefunden. Speichere in Datei...")
        save_errors_to_file(errors, missing_station_ids, MISSING_REFERENCES_FILE)
    else:
        print("\nAlle station_id-Werte sind korrekt referenziert.")

if __name__ == "__main__":
    main()

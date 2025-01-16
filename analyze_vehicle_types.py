import os
import json
from collections import Counter

# Pfade zu den Ordnern
DATA_FOLDER = r"C:\Projekte\KNIME_Aufgabe\data"
OUTPUT_FILE = os.path.join(DATA_FOLDER, "vehicle_type_analysis.txt")

# Funktion zur Analyse der vehicle_type_id-Werte
def analyze_vehicle_types(data_folder):
    vehicle_types = Counter()

    for filename in os.listdir(data_folder):
        if filename.endswith(".json"):
            file_path = os.path.join(data_folder, filename)
            try:
                with open(file_path, 'r') as f:
                    data = json.load(f)

                    # Prüfe "vehicle_types_available"
                    stations = data.get("data", {}).get("stations", [])
                    for station in stations:
                        if "vehicle_types_available" in station:
                            for entry in station["vehicle_types_available"]:
                                vehicle_type_id = entry.get("vehicle_type_id")
                                if isinstance(vehicle_type_id, str):
                                    vehicle_types[vehicle_type_id] += 1

                        # Prüfe "vehicle_docks_available"
                        if "vehicle_docks_available" in station:
                            for entry in station["vehicle_docks_available"]:
                                vehicle_type_ids = entry.get("vehicle_type_ids", [])
                                if isinstance(vehicle_type_ids, list):
                                    for vt_id in vehicle_type_ids:
                                        if isinstance(vt_id, str):
                                            vehicle_types[vt_id] += 1

            except json.JSONDecodeError as e:
                print(f"Fehler beim Laden von {filename}: Ungültiges JSON-Format")
            except Exception as e:
                print(f"Unerwarteter Fehler in {filename}: {e}")

    return vehicle_types

# Funktion zum Speichern der Ergebnisse in einer Datei
def save_results_to_file(vehicle_types, output_file):
    try:
        with open(output_file, 'w') as f:
            f.write("Analyse der vehicle_type_id-Werte:\n\n")
            f.write(f"Gefundene Werte: {len(vehicle_types)}\n\n")
            f.write("Wert - Häufigkeit:\n")
            for vehicle_type, count in vehicle_types.items():
                f.write(f"{vehicle_type}: {count}\n")
        print(f"Ergebnisse wurden in {output_file} gespeichert.")
    except Exception as e:
        print(f"Fehler beim Schreiben der Datei {output_file}: {e}")

# Hauptfunktion
def main():
    print("Starte Analyse der vehicle_type_id-Werte...")
    vehicle_types = analyze_vehicle_types(DATA_FOLDER)
    if vehicle_types:
        save_results_to_file(vehicle_types, OUTPUT_FILE)
    else:
        print("Keine vehicle_type_id-Werte gefunden.")

if __name__ == "__main__":
    main()

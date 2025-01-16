import os
import json

# Pfad zum Datenordner
DATA_FOLDER = r"C:\Projekte\KNIME_Aufgabe\data"

# Funktion zur Validierung einer einzelnen Station
def validate_station(station):
    errors = []

    # Pflichtfelder und deren Typen
    required_fields = {
        "station_id": str,
        "is_installed": bool,
        "is_renting": bool,
        "is_returning": bool,
        "last_reported": int,
        "num_bikes_available": int
    }

    # Überprüfung der Pflichtfelder
    for field, field_type in required_fields.items():
        if field not in station:
            errors.append(f"Fehlendes Pflichtfeld: {field}")
        elif not isinstance(station[field], field_type):
            errors.append(f"Falscher Typ für {field}: Erwartet {field_type.__name__}, erhalten {type(station[field]).__name__}")

    # Zusätzliche Bedingungen für numerische Felder
    numeric_fields = [
        "num_bikes_available",
        "num_bikes_disabled"
    ]
    for field in numeric_fields:
        if field in station and isinstance(station[field], int) and station[field] < 0:
            errors.append(f"Wert von {field} darf nicht negativ sein")

    # Prüfung der Arrays "vehicle_types_available" und "vehicle_docks_available"
    if "vehicle_types_available" in station:
        for entry in station["vehicle_types_available"]:
            if not isinstance(entry.get("vehicle_type_id"), str):
                errors.append(f"Falscher Typ für vehicle_type_id in vehicle_types_available: Erwartet str")
            if not isinstance(entry.get("count"), int) or entry["count"] < 0:
                errors.append(f"Falscher oder negativer Wert für count in vehicle_types_available")

    if "vehicle_docks_available" in station:
        for entry in station["vehicle_docks_available"]:
            if not isinstance(entry.get("vehicle_type_ids"), list) or not all(isinstance(i, str) for i in entry["vehicle_type_ids"]):
                errors.append(f"Falscher Typ für vehicle_type_ids in vehicle_docks_available: Erwartet Liste von Strings")
            if not isinstance(entry.get("count"), int) or entry["count"] < 0:
                errors.append(f"Falscher oder negativer Wert für count in vehicle_docks_available")

    # Logikprüfung: Summe der counts in vehicle_types_available darf nicht größer sein als num_bikes_available
    if "vehicle_types_available" in station:
        total_vehicle_count = sum(entry.get("count", 0) for entry in station["vehicle_types_available"] if isinstance(entry.get("count"), int))
        if total_vehicle_count > station.get("num_bikes_available", 0):
            errors.append("Summe der counts in vehicle_types_available überschreitet num_bikes_available")

    return errors

# Schema-Validierungsfunktion
def validate_json_schema(folder):
    all_errors = []

    for filename in os.listdir(folder):
        if filename.endswith(".json"):
            file_path = os.path.join(folder, filename)
            try:
                with open(file_path, 'r') as f:
                    data = json.load(f)

                    # Validierung der stations
                    stations = data.get("data", {}).get("stations", [])
                    for station in stations:
                        errors = validate_station(station)
                        if errors:
                            all_errors.append((filename, station.get("station_id", "unknown"), errors))

            except json.JSONDecodeError as e:
                all_errors.append((filename, "", [f"Ungültiges JSON-Format: {e.msg}"]))
            except Exception as e:
                all_errors.append((filename, "", [f"Unerwarteter Fehler: {e}"]))

    return all_errors

# Hauptfunktion
def main():
    print("Überprüfe JSON-Dateien im Ordner:", DATA_FOLDER)
    errors = validate_json_schema(DATA_FOLDER)

    if errors:
        print("\nFehler in JSON-Dateien:")
        for filename, station_id, error_list in errors:
            print(f"Datei: {filename}, Station: {station_id}")
            for error in error_list:
                print(f"  - {error}")
    else:
        print("\nAlle JSON-Dateien entsprechen dem Schema.")

if __name__ == "__main__":
    main()

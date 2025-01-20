import knime.scripting.io as knio
import pandas as pd
import json
from collections import Counter

# Eingabetabelle aus dem List Files/Folders-Knoten
input_table = knio.input_tables[0].to_pandas()

# Überprüfen, ob die Tabelle Daten enthält
if input_table.shape[0] == 0:
    raise ValueError("Die Eingabetabelle ist leer. Bitte überprüfen Sie den vorherigen Knoten.")

# Spalte mit Dateipfaden extrahieren (Path-Eigenschaft)
file_paths = [str(row['Path'].path) for _, row in input_table.iterrows()]

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

# Funktion zur Häufigkeitsanalyse von String-Feldern
def get_most_frequent_value(field, neighbors):
    values = []
    for neighbor in neighbors:
        for station in neighbor.get("data", {}).get("stations", []):
            value = station.get(field)
            if isinstance(value, str):
                values.append(value)
    if values:
        return Counter(values).most_common(1)[0][0]  # Häufigster Wert
    return "unknown"  # Standardwert, falls keine Strings gefunden werden

# Funktion zur Reparatur einer Station
def repair_station(station, neighbors):
    string_fields = ["station_id", "vehicle_type_id"]  # String-Felder, die repariert werden sollen
    for field in string_fields:
        if field not in station or not isinstance(station[field], str):
            station[field] = get_most_frequent_value(field, neighbors)

# Funktion zum Laden einer Datei
def load_json_file(file_path):
    try:
        with open(file_path, 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"Fehler beim Laden der Datei {file_path}: {e}")
        return {}

# Listen für valide und fehlerhafte Dateien
valid_files = []
invalid_files = []
error_messages = []

# Dateien verarbeiten
for i, file_path in enumerate(file_paths):
    neighbors = []

    # Bestimme Nachbardateien
    if i > 0:
        neighbors.append(load_json_file(file_paths[i - 1]))
    if i < len(file_paths) - 1:
        neighbors.append(load_json_file(file_paths[i + 1]))

    try:
        data = load_json_file(file_path)
        stations = data.get("data", {}).get("stations", [])

        for station in stations:
            # Validierung der Station
            station_errors = validate_station(station)

            # Reparatur der Strings
            if station_errors:
                repair_station(station, neighbors)
                station_errors = validate_station(station)

            if station_errors:
                invalid_files.append(file_path)
                error_messages.append("; ".join(station_errors))
                break
        else:
            valid_files.append(file_path)
    except Exception as e:
        invalid_files.append(file_path)
        error_messages.append(str(e))

# Listen ausgleichen, damit sie die gleiche Länge haben
max_length = max(len(valid_files), len(invalid_files), len(error_messages))

valid_files.extend([""] * (max_length - len(valid_files)))
invalid_files.extend([""] * (max_length - len(invalid_files)))
error_messages.extend([""] * (max_length - len(error_messages)))

# Ergebnisse in einen DataFrame schreiben
output_df = pd.DataFrame({
    'Valid Files': valid_files,
    'Invalid Files': invalid_files,
    'Error Messages': error_messages
})

# Ergebnis ausgeben
knio.output_tables[0] = knio.Table.from_pandas(output_df)

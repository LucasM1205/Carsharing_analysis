import knime.scripting.io as knio
import pandas as pd
import json

# Eingabetabelle einlesen
input_table = knio.input_tables[0].to_pandas()

# Überprüfen, ob die Tabelle leer ist
if input_table.empty:
    raise ValueError("Die Eingabetabelle ist leer. Keine Dateien zum Einlesen.")

# Spalten 'File Path' extrahieren
file_paths = input_table["File Path"].tolist()

# Liste zur Speicherung der Daten
all_data = []

# JSON-Dateien einlesen
for file_path in file_paths:
    try:
        with open(file_path, 'r') as f:
            data = json.load(f)
            stations = data.get("data", {}).get("stations", [])
            for station in stations:
                # Initialisiere Standardwerte für die Felder
                station_id = station.get("station_id", "unknown")
                num_bikes_available = station.get("num_bikes_available", 0)
                is_installed = station.get("is_installed", False)
                is_renting = station.get("is_renting", False)
                is_returning = station.get("is_returning", False)
                last_reported = station.get("last_reported", 0)
                
                # Verarbeite 'vehicle_types_available', falls vorhanden
                vehicle_types = station.get("vehicle_types_available", [])
                if vehicle_types and isinstance(vehicle_types, list):
                    for vehicle in vehicle_types:
                        vehicle_type_id = vehicle.get("vehicle_type_id", "unknown")
                        count = vehicle.get("count", 0)
                        # Speichere die Daten
                        all_data.append({
                            "station_id": station_id,
                            "num_bikes_available": num_bikes_available,
                            "is_installed": is_installed,
                            "is_renting": is_renting,
                            "is_returning": is_returning,
                            "last_reported": last_reported,
                            "vehicle_type_id": vehicle_type_id,
                            "counts": count
                        })
                else:
                    # Falls keine Fahrzeuge vorhanden sind, füge einen leeren Eintrag hinzu
                    all_data.append({
                        "station_id": station_id,
                        "num_bikes_available": num_bikes_available,
                        "is_installed": is_installed,
                        "is_renting": is_renting,
                        "is_returning": is_returning,
                        "last_reported": last_reported,
                        "vehicle_type_id": "unknown",
                        "counts": 0
                    })
    except json.JSONDecodeError as e:
        print(f"Fehler beim Parsen von {file_path}: {e}")
    except Exception as e:
        print(f"Allgemeiner Fehler beim Einlesen von {file_path}: {e}")

# Überprüfen, ob Daten vorliegen
if not all_data:
    raise ValueError("Keine Daten aus den JSON-Dateien gelesen.")

# Daten in DataFrame umwandeln
output_df = pd.DataFrame(all_data)

# Ausgabe an KNIME zurückgeben
knio.output_tables[0] = knio.Table.from_pandas(output_df)

import knime.scripting.io as knio
import os
import json
import pandas as pd

# Eingabetabelle aus dem vorherigen Python-Knoten
input_table = knio.input_tables[0].to_pandas()

# Prüfe, ob die Spalte für fehlerhafte Dateien existiert (ersetze 'Invalid Files' mit dem richtigen Spaltennamen)
if 'Invalid Files' not in input_table.columns:
    raise KeyError("Die erwartete Spalte 'Invalid Files' wurde nicht gefunden. Verfügbare Spalten: " + ", ".join(input_table.columns))

# Verzeichnisse
error_folder = r"C:\Projekte\KNIME_Aufgabe\error_files"
data_folder = r"C:\Projekte\KNIME_Aufgabe\data"
repaired_folder = r"C:\Projekte\KNIME_Aufgabe\repaired_files"
os.makedirs(repaired_folder, exist_ok=True)

# Liste aller Dateien im Datenverzeichnis
all_files = sorted([f for f in os.listdir(data_folder) if f.endswith(".json")])

# Funktion zur Berechnung des Mittelwerts für numerische Felder
def calculate_average(value1, value2):
    if isinstance(value1, (int, float)) and isinstance(value2, (int, float)):
        return (value1 + value2) // 2
    return value1 if value1 else value2

# Funktion zur Reparatur einer fehlerhaften Datei
def repair_file(file_name, all_files, data_folder, repaired_folder):
    current_index = all_files.index(file_name)
    prev_file = all_files[current_index - 1] if current_index > 0 else None
    next_file = all_files[current_index + 1] if current_index < len(all_files) - 1 else None

    repaired_data = {"data": {"stations": []}}

    # Laden der Nachbardateien
    for neighbor_file in [prev_file, next_file]:
        if neighbor_file:
            try:
                with open(os.path.join(data_folder, neighbor_file), 'r') as file:
                    neighbor_data = json.load(file)
                    if "data" in neighbor_data and "stations" in neighbor_data["data"]:
                        repaired_data["data"]["stations"].extend(neighbor_data["data"]["stations"])
            except Exception as e:
                print(f"Fehler beim Laden der Nachbardatei {neighbor_file}: {e}")

    # Mittelwertbildung oder Übernehmen der Werte
    for station in repaired_data["data"]["stations"]:
        station["num_bikes_available"] = calculate_average(
            station.get("num_bikes_available"),
            station.get("num_bikes_available")
        )
        station["num_bikes_disabled"] = calculate_average(
            station.get("num_bikes_disabled"),
            station.get("num_bikes_disabled")
        )

    # Speichern der reparierten Datei
    repaired_path = os.path.join(repaired_folder, file_name)
    with open(repaired_path, 'w') as repaired_file:
        json.dump(repaired_data, repaired_file, indent=4)

# Verarbeitung der fehlerhaften Dateien
for index, row in input_table.iterrows():
    error_file = row["Invalid Files"]  # Nutze hier den tatsächlichen Spaltennamen für fehlerhafte Dateien
    if os.path.basename(error_file) in all_files:
        repair_file(os.path.basename(error_file), all_files, data_folder, repaired_folder)

# Ausgabe an KNIME weitergeben
output_table = pd.DataFrame({
    "Repaired Files": [os.path.join(repaired_folder, f) for f in os.listdir(repaired_folder)],
    "Status": ["Repaired" for _ in os.listdir(repaired_folder)]
})
knio.output_tables[0] = knio.Table.from_pandas(output_table)

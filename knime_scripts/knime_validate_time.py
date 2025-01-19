import knime.scripting.io as knio
import os
import re
import pandas as pd
from datetime import datetime, timedelta

# Verzeichnis der Dateien
DATA_FOLDER = r"C:\Projekte\KNIME_Aufgabe\data"

# Funktion zum Extrahieren der Unix-Timestamps aus den Dateinamen
def extract_timestamps(folder):
    timestamps = []
    for filename in os.listdir(folder):
        match = re.search(r"car_(\d{2}-\d{2}-\d{2})_(\d{2}_\d{2})\.json", filename)
        if match:
            date_part = match.group(1)
            time_part = match.group(2).replace("_", ":")
            date_time = datetime.strptime(f"{date_part} {time_part}", "%y-%m-%d %H:%M")
            timestamps.append((filename, int(date_time.timestamp())))
    return sorted(timestamps, key=lambda x: x[1])

# Funktion zum Finden fehlender Dateien basierend auf Zeitstempeln
def find_missing_files(timestamps):
    missing = []
    for i in range(len(timestamps) - 1):
        current_time = timestamps[i][1]
        next_time = timestamps[i + 1][1]
        if next_time - current_time > 3600:  # Unterschied größer als 1 Stunde
            missing_count = (next_time - current_time) // 3600
            for j in range(1, missing_count):
                missing_time = current_time + j * 3600
                missing.append(missing_time)
    return missing

# Funktion zum Formatieren fehlender Dateien
def format_missing_files(missing_times):
    missing_files = []
    for time in missing_times:
        missing_date = datetime.fromtimestamp(time)
        missing_files.append(f"car_{missing_date.strftime('%y-%m-%d')}_{missing_date.strftime('%H_%M')}.json")
    return missing_files

# Dateien analysieren
print(f"Analysiere JSON-Dateien im Ordner: {DATA_FOLDER}")

if not os.path.exists(DATA_FOLDER):
    raise ValueError(f"Das Verzeichnis {DATA_FOLDER} existiert nicht.")

timestamps = extract_timestamps(DATA_FOLDER)

if not timestamps:
    raise ValueError(f"Keine Dateien im erwarteten Format im Ordner: {DATA_FOLDER}")

missing_times = find_missing_files(timestamps)
missing_files = format_missing_files(missing_times)

# Ergebnisse in DataFrame schreiben
output_df = pd.DataFrame({
    "Missing Files": missing_files
})

# Ausgabe des DataFrame an den ersten Output-Port
knio.output_tables[0] = knio.Table.from_pandas(output_df)

print("Analyse abgeschlossen.")

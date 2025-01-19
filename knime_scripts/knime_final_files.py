import knime.scripting.io as knio
import os
import pandas as pd

# Verzeichnisse
data_folder = r"C:\Projekte\KNIME_Aufgabe\data"
repaired_folder = r"C:\Projekte\KNIME_Aufgabe\repaired_files"

# Liste aller Dateien im `data`-Ordner
data_files = {os.path.basename(f): os.path.join(data_folder, f) for f in os.listdir(data_folder) if f.endswith(".json")}

# Liste aller Dateien im `repaired_files`-Ordner
repaired_files = {os.path.basename(f): os.path.join(repaired_folder, f) for f in os.listdir(repaired_folder) if f.endswith(".json")}

# Zusammenführen der Datenbasis
final_files = {}
for file_name, file_path in data_files.items():
    # Falls eine reparierte Version existiert, wird diese bevorzugt
    if file_name in repaired_files:
        final_files[file_name] = repaired_files[file_name]
    else:
        final_files[file_name] = file_path

# DataFrame mit finaler Datenbasis
output_table = pd.DataFrame({
    "File Name": list(final_files.keys()),
    "File Path": list(final_files.values()),
    "Source": ["Repaired" if file_name in repaired_files else "Original" for file_name in final_files.keys()]
})

# Ausgabe in KNIME-Tabellenformat
knio.output_tables[0] = knio.Table.from_pandas(output_table)

import json
import pandas as pd
import folium

# Pfad zu den Dateien
data_folder = r"C:\Projekte\KNIME_Aufgabe\visualization"
status_file = f"{data_folder}\\station_status.json"
info_file = f"{data_folder}\\station_information.json"

# Dateien einlesen
try:
    with open(status_file, "r") as sf, open(info_file, "r") as inf:
        status_data = json.load(sf)
        info_data = json.load(inf)
except FileNotFoundError as e:
    print(f"Dateien konnten nicht geladen werden: {e}")
    exit()

# Daten extrahieren
status_df = pd.DataFrame(status_data["data"]["stations"])
info_df = pd.DataFrame(info_data["data"]["stations"])

# Zusammenführen der Daten anhand der station_id
merged_df = pd.merge(info_df, status_df, on="station_id", how="inner")

# Karte erstellen (mittlerer Punkt der Stationen)
map_center = [merged_df["lat"].mean(), merged_df["lon"].mean()]
map = folium.Map(location=map_center, zoom_start=12)

# Marker hinzufügen
for _, row in merged_df.iterrows():
    popup_info = (
        f"<b>{row['name']}</b><br>"
        f"Bikes verfügbar: {row['num_bikes_available']}<br>"
        f"Station ID: {row['station_id']}"
    )
    marker_color = "blue" if row["num_bikes_available"] > 0 else "red"
    folium.Marker(
        location=[row["lat"], row["lon"]],
        popup=popup_info,
        icon=folium.Icon(color=marker_color),
    ).add_to(map)

# Karte speichern
output_file = f"{data_folder}\\map.html"
map.save(output_file)
print(f"Karte wurde erstellt und unter {output_file} gespeichert.")

import os
import json
import pandas as pd
import folium

# Analyse für Zeitraum: 21.06.2024 - 12.11.2024

# Ordnerpfade
data_folder = r"C:\Projekte\KNIME_Aufgabe\data"
repaired_folder = r"C:\Projekte\KNIME_Aufgabe\repaired_files"
info_file = r"C:\Projekte\KNIME_Aufgabe\visualization\station_information.json"

# Liste fehlerhafter Dateien
error_files = {
    "car_24-06-30_01_00.json",
    "car_24-09-21_10_00.json",
    "car_24-09-22_14_00.json",
    "car_24-09-27_15_00.json",
}

# Dictionary für die Dateipfade erstellen
file_dict = {}
for file in os.listdir(data_folder):
    if file in error_files:
        repaired_file_path = os.path.join(repaired_folder, file)
        if os.path.exists(repaired_file_path):
            file_dict[file] = repaired_file_path
        else:
            print(f"Warnung: Reparierte Datei {file} fehlt im Ordner {repaired_folder}")
    else:
        file_dict[file] = os.path.join(data_folder, file)

# station_information.json laden
with open(info_file, "r") as f:
    info_data = json.load(f)
info_df = pd.DataFrame(info_data["data"]["stations"])

# Daten aggregieren
station_data = []

for file_name, file_path in file_dict.items():
    try:
        with open(file_path, "r") as f:
            data = json.load(f)
            stations = data.get("data", {}).get("stations", [])
            for station in stations:
                station_data.append({
                    "station_id": station["station_id"],
                    "num_bikes_available": station.get("num_bikes_available", 0),
                })
    except Exception as e:
        print(f"Fehler beim Verarbeiten der Datei {file_name}: {e}")

# DataFrame aus den Stationsdaten erstellen
station_df = pd.DataFrame(station_data)

# Durchschnitt der Fahrzeuge pro Station berechnen
avg_bikes_df = station_df.groupby("station_id")["num_bikes_available"].mean().reset_index()
avg_bikes_df.rename(columns={"num_bikes_available": "avg_bikes_available"}, inplace=True)

# Durchschnittsdaten mit station_information verknüpfen
merged_df = pd.merge(info_df, avg_bikes_df, on="station_id", how="inner")

# Top 5 Stationen auswählen
top_5_stations = merged_df.nlargest(5, "avg_bikes_available")

# Karte erstellen
map_center = [merged_df["lat"].mean(), merged_df["lon"].mean()]
top_5_map = folium.Map(location=map_center, zoom_start=12)

# Marker für alle Stationen hinzufügen
for _, row in merged_df.iterrows():
    popup_info = (
        f"<b>{row['name']}</b><br>"
        f"Durchschnittlich verfügbare Fahrzeuge: {row['avg_bikes_available']:.2f}<br>"
        f"Station ID: {row['station_id']}"
    )
    folium.CircleMarker(
        location=[row["lat"], row["lon"]],
        radius=5,
        popup=popup_info,
        color="gray",
        fill=True,
        fill_opacity=0.5,
    ).add_to(top_5_map)

# Marker für die Top 5 Stationen hervorheben (mit Platzierung als Icon)
for rank, (_, row) in enumerate(top_5_stations.iterrows(), start=1):
    popup_info = (
        f"<b>{row['name']} (Platz {rank})</b><br>"
        f"Durchschnittlich verfügbare Fahrzeuge: {row['avg_bikes_available']:.2f}<br>"
        f"Station ID: {row['station_id']}"
    )
    folium.Marker(
        location=[row["lat"], row["lon"]],
        popup=popup_info,
        icon=folium.DivIcon(
            html=f"""
                <div style="font-size:12px; font-weight:bold; color:white; text-align:center;
                            background-color:blue; border-radius:50%; width:20px; height:20px; line-height:20px;">
                    {rank}
                </div>
            """
        ),
    ).add_to(top_5_map)

# Karte speichern
output_file = r"C:\Projekte\KNIME_Aufgabe\visualization\top_5_stations_map_with_rank.html"
top_5_map.save(output_file)
print(f"Karte wurde gespeichert unter: {output_file}")

import json
import pandas as pd
import folium
import requests
from datetime import datetime

# API-URL und station_information.json Pfad
status_url = "https://api.mobidata-bw.de/sharing/gbfs/v2/deer/station_status"
info_file = r"C:\Projekte\KNIME_Aufgabe\visualization\station_information.json"

# station_information.json laden
with open(info_file, "r") as f:
    info_data = json.load(f)
info_df = pd.DataFrame(info_data["data"]["stations"])

# Funktion zum Abrufen der Live-Daten und Erstellen der Karte
def update_map():
    try:
        # Live-Daten abrufen
        response = requests.get(status_url)
        if response.status_code == 200:
            status_data = response.json()
            status_df = pd.DataFrame(status_data["data"]["stations"])
            last_updated = status_data.get("last_updated", int(datetime.now().timestamp()))
            readable_time = datetime.fromtimestamp(last_updated).strftime('%Y-%m-%d %H:%M:%S')

            # Postleitzahl aus der Adresse extrahieren (erste zwei Ziffern)
            info_df["postal_code_prefix"] = info_df["post_code"].str[:2]
            if info_df["postal_code_prefix"].isnull().all():
                print("Keine gültigen Postleitzahlen gefunden.")
                return

            # Live-Daten mit station_information-Daten verknüpfen
            merged_df = pd.merge(info_df, status_df, on="station_id", how="inner")

            # Debugging: Überprüfe Frankfurt
            if "DER:Station:62f0f33bf8f249177b1e3245" not in merged_df["station_id"].values:
                print("Frankfurt fehlt in merged_df.")
                print("Live-Daten:")
                print(status_df[status_df["station_id"] == "DER:Station:62f0f33bf8f249177b1e3245"])
                print("Referenzdaten:")
                print(info_df[info_df["station_id"] == "DER:Station:62f0f33bf8f249177b1e3245"])

            # Gruppieren nach den ersten beiden Ziffern der Postleitzahl
            grouped_df = merged_df.groupby("postal_code_prefix").agg(
                avg_bikes_available=("num_bikes_available", "mean"),
                avg_lat=("lat", "mean"),
                avg_lon=("lon", "mean"),
            ).reset_index()

            # Debugging: Region 60 prüfen
            print("Region 60:")
            print(grouped_df[grouped_df["postal_code_prefix"] == "60"])

            # Überprüfen, ob die Gruppierung erfolgreich war
            if grouped_df.empty:
                print("Keine gültigen Gruppierungsdaten gefunden.")
                return

            # Karte erstellen
            map_center = [grouped_df["avg_lat"].mean(), grouped_df["avg_lon"].mean()]
            region_map = folium.Map(location=map_center, zoom_start=10)

            # Marker hinzufügen
            for _, row in grouped_df.iterrows():
                popup_info = (
                    f"<b>Region: {row['postal_code_prefix']}xxx</b><br>"
                    f"Durchschnittlich verfügbare Fahrzeuge: {row['avg_bikes_available']:.2f}<br>"
                )
                # Neues Farbschema basierend auf der durchschnittlichen Verfügbarkeit
                if row["avg_bikes_available"] < 1:
                    color = "red"
                elif row["avg_bikes_available"] <= 1.5:
                    color = "yellow"
                else:
                    color = "green"

                folium.CircleMarker(
                    location=[row["avg_lat"], row["avg_lon"]],
                    radius=10,
                    popup=popup_info,
                    color=color,
                    fill=True,
                    fill_opacity=0.7,
                ).add_to(region_map)

            # Karte speichern
            output_file = r"C:\Projekte\KNIME_Aufgabe\visualization\region_map.html"
            region_map.save(output_file)
            print(f"Karte wurde gespeichert unter: {output_file}")
            print(f"Letzte Aktualisierung: {readable_time}")
        else:
            print(f"Fehler beim Abrufen der Live-Daten: {response.status_code}")
    except Exception as e:
        print(f"Fehler beim Aktualisieren der Karte: {e}")

# Karte aktualisieren
update_map()

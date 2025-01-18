import json
import pandas as pd
import folium
import requests
from datetime import datetime, timezone

# API-URL und station_information.json Pfad
status_url = "https://api.mobidata-bw.de/sharing/gbfs/v2/deer/station_status"
info_file = r"C:\Projekte\KNIME_Aufgabe\visualization\station_information.json"

# Lade die station_information-Daten (statische Datei)
try:
    with open(info_file, "r") as inf:
        info_data = json.load(inf)
except FileNotFoundError as e:
    print(f"Datei station_information.json konnte nicht geladen werden: {e}")
    exit()

info_df = pd.DataFrame(info_data["data"]["stations"])

# Funktion zum Abrufen von Live-Daten und Erstellen der Karte
def update_map():
    try:
        # Live-Daten abrufen
        response = requests.get(status_url)
        if response.status_code == 200:
            status_data = response.json()
            # Hole den last_updated-Wert aus den API-Daten
            last_updated = status_data.get("last_updated", int(datetime.now().timestamp()))
            readable_time = datetime.fromtimestamp(last_updated, tz=timezone.utc).strftime('%Y-%m-%d %H:%M:%S')

            # Daten zu Stationen
            status_df = pd.DataFrame(status_data["data"]["stations"])

            # Daten zusammenführen
            merged_df = pd.merge(info_df, status_df, on="station_id", how="inner")

            # Karte erstellen
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

            # HTML mit Button generieren
            update_script = f"""
                <script>
                    function reloadPage() {{
                        const currentUrl = window.location.href.split('?')[0];
                        const timestamp = "{last_updated}";
                        window.location.href = currentUrl + "?v=" + timestamp;
                    }}
                </script>
                <div style="text-align:center; margin:20px;">
                    <p style="font-size:16px; font-weight:bold;">Letzte Aktualisierung: {readable_time}</p>
                    <button onclick="reloadPage()" style="padding:10px 20px; font-size:16px; background-color:#4CAF50; color:white; border:none; border-radius:5px; cursor:pointer;">
                        Aktualisieren
                    </button>
                </div>
            """
            map.get_root().html.add_child(folium.Element(update_script))

            # Karte speichern
            output_file = r"C:\Projekte\KNIME_Aufgabe\visualization\map.html"
            map.save(output_file)
            print(f"Karte wurde aktualisiert und unter {output_file} gespeichert.")
        else:
            print(f"Fehler beim Abrufen der Live-Daten: {response.status_code}")
    except Exception as e:
        print(f"Fehler beim Aktualisieren der Karte: {e}")
        with open(r"C:\Projekte\KNIME_Aufgabe\visualization\error_log.txt", "a") as log_file:
            log_file.write(f"{datetime.now()}: {e}\n")

# Karte einmalig aktualisieren
update_map()

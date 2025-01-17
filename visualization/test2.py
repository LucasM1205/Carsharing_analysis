import json
import pandas as pd
import folium
import requests
from datetime import datetime, timedelta
import time

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

            # HTML mit Countdown generieren
            refresh_time = datetime.now() + timedelta(minutes=1)
            countdown_script = f"""
                <script>
                    function startCountdown() {{
                        const refreshTime = new Date("{refresh_time.isoformat()}").getTime();
                        const interval = setInterval(function() {{
                            const now = new Date().getTime();
                            const distance = refreshTime - now;

                            if (distance <= 0) {{
                                clearInterval(interval);
                                location.reload(true); // Seite neu laden
                            }} else {{
                                const minutes = Math.floor((distance % (1000 * 60 * 60)) / (1000 * 60));
                                const seconds = Math.floor((distance % (1000 * 60)) / 1000);
                                document.getElementById("countdown").innerHTML = minutes + "m " + seconds + "s bis zum nächsten Update";
                            }}
                        }}, 1000);
                    }}
                    window.onload = startCountdown;
                </script>
                <div id="countdown" style="font-size:20px; font-weight:bold; text-align:center; margin:10px;">Lade...</div>
            """
            map.get_root().html.add_child(folium.Element(countdown_script))

            # Karte speichern
            output_file = r"C:\Projekte\KNIME_Aufgabe\visualization\map.html"
            map.save(output_file)
            print(f"Karte wurde aktualisiert und unter {output_file} gespeichert.")
        else:
            print(f"Fehler beim Abrufen der Live-Daten: {response.status_code}")
    except Exception as e:
        print(f"Fehler beim Aktualisieren der Karte: {e}")

# Endlosschleife für Updates alle 60 Sekunden
try:
    while True:
        update_map()
        time.sleep(60)  # Warte 60 Sekunden bis zum nächsten Update
except KeyboardInterrupt:
    print("Programm beendet.")

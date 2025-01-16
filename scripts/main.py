import os
import re
from datetime import datetime, timedelta

# Pfad zum Datenordner
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
        missing_files.append(f"car_{missing_date.strftime('%y-%m-%d_%H_%M')}.json")
    return missing_files

# Funktion zum Überprüfen der Wochentage und Generieren der fehlenden JSON-Dateien
def check_weekday_coverage_with_files(timestamps):
    # Start- und Endzeitpunkte aus den vorhandenen Timestamps
    start_time = datetime.fromtimestamp(timestamps[0][1])
    end_time = datetime.fromtimestamp(timestamps[-1][1])

    # Alle vorhandenen Daten zu einem Set von Datum-Wochentag-Paaren zusammenfassen
    existing_days = set()
    for _, timestamp in timestamps:
        date = datetime.fromtimestamp(timestamp)
        existing_days.add((date.date(), date.strftime("%A")))  # Tuple: (Datum, Wochentag)

    # Fehlende Wochentage pro Woche ermitteln
    missing_weekdays_with_files = {}
    current_time = start_time

    while current_time <= end_time:
        year_week = current_time.strftime("%Y-W%U")  # Jahr und Kalenderwoche
        weekday = current_time.strftime("%A")  # Wochentag

        # Prüfen, ob dieses Datum-Wochentag-Paar existiert
        if (current_time.date(), weekday) not in existing_days:
            if year_week not in missing_weekdays_with_files:
                missing_weekdays_with_files[year_week] = {}
            if weekday not in missing_weekdays_with_files[year_week]:
                missing_weekdays_with_files[year_week][weekday] = []

            # Generiere stündliche Dateien für den fehlenden Tag
            for hour in range(24):
                missing_file = f"car_{current_time.strftime('%y-%m-%d')}_{hour:02}_00.json"
                missing_weekdays_with_files[year_week][weekday].append(missing_file)

        # Zum nächsten Tag gehen
        current_time += timedelta(days=1)

    return missing_weekdays_with_files

# Hauptfunktion
def main():
    print("Analysiere JSON-Dateien im Ordner:", DATA_FOLDER)

    # Timestamps extrahieren
    timestamps = extract_timestamps(DATA_FOLDER)
    if not timestamps:
        print("Keine Dateien gefunden.")
        return

    # Fehlende Dateien finden
    missing_times = find_missing_files(timestamps)
    missing_files = format_missing_files(missing_times)

    # Ausgabe fehlender Dateien
    if missing_files:
        print("Fehlende Dateien:")
        for file in missing_files:
            print(file)
    else:
        print("Es fehlen keine Dateien.")

    # Wochentagsprüfung mit fehlenden JSON-Dateien
    missing_weekdays_with_files = check_weekday_coverage_with_files(timestamps)
    if missing_weekdays_with_files:
        print("\nFehlende Wochentage und JSON-Dateien pro Woche:")
        for week, days in missing_weekdays_with_files.items():
            print(f"Woche {week}:")
            for day, files in days.items():
                print(f"  {day}:")
                for file in files:
                    print(f"    {file}")
    else:
        print("\nAlle Wochen haben vollständige Wochentagsabdeckung.")

if __name__ == "__main__":
    main()

#Als nächstes leeren Platzhalter für die fehlenden Dateien generieren?
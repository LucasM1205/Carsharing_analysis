# Carsharing Analysis

Dieses Repository enthält die vollständige Implementierung einer Analyse und Visualisierung von Carsharing-Daten, basierend auf einer Kombination aus KNIME-Workflows und Python-Skripten. Ziel des Projekts ist es, Carsharing-Daten zu bereinigen, zu validieren und geografisch darzustellen, um Muster und Erkenntnisse aus den bereitgestellten Live- und Archivdaten zu gewinnen

**Hinweis**: Der hauptsächliche KNIME-Workflow befindet sich in 5. knime_file und kann dort in Form eines Zip-Archives heruntergeladen werden

## Projektstruktur

Die Verzeichnisstruktur des Projekts ist wie folgt aufgebaut:

### **1. .venv**
- Enthält die virtuelle Umgebung für Python, in der die erforderlichen Bibliotheken installiert sind (z. B. `folium`, `pandas`, `requests`)
- **Hinweis**: Die virtuelle Umgebung ist optional und sollte neu erstellt werden, falls das Projekt auf einem anderen System verwendet wird

### **2. .vscode**
- Konfigurationsdateien für Visual Studio Code, einschließlich Debug-Einstellungen und Python-Umgebungsreferenzen

### **3. data**
- Enthält die **unveränderten Archivdaten** im JSON-Format, die ursprünglich aus der MobiDataBW-API extrahiert wurden
- Diese Daten dienen als Grundlage für die Analyse und Visualisierung
- **Hinweis**: Das Archiv ist wegen des Umfangs in diesem Repository nicht vollständig

### **4. error_files**
- Beinhaltet die **fehlerhaften Dateien**, die bei der Validierung in KNIME als ungültig klassifiziert wurden
- Diese Dateien wurden separat abgelegt, um die Sanierung zu ermöglichen

### **5. knime_file**
- Enthält den exportierten **KNIME-Workflow**, die in der Analyse verwendet wurde
- Dieser Workflow bildet die logischen Schritte für die Datenbereinigung und -validierung ab

### **6. knime_scripts**
- Python-Skripte, die direkt in KNIME-Knoten eingebettet wurden
- Diese Skripte umfassen die Validierungslogik, das Lesen von JSON-Dateien und die Integration mit den KNIME-Workflows

### **7. references**
- Dokumentationen und Referenzen, einschließlich des verwendeten GBFS-Standards (General Bikeshare Feed Specification)
- Dient als Grundlage für die Definition von Validierungs- und Sanierungskriterien

### **8. repaired_files**
- Enthält die **reparierten JSON-Dateien**, die auf Basis der in KNIME implementierten Sanierungslogik generiert wurden
- Diese Dateien ersetzen die fehlerhaften Dateien in den Analysen

### **9. scripts**
- Python-Skripte zur Unterstützung von Datenverarbeitungs- und Validierungsaufgaben außerhalb von KNIME
- Hier wurden erste Tests und Proof-of-Concepts durchgeführt

### **10. visualization**
- Python-Skripte zur Erstellung interaktiver Karten basierend auf den Live- und Archivdaten
- Die Karten wurden mit der `folium`-Bibliothek erstellt und als HTML-Dateien ausgegeben

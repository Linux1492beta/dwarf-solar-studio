# ☀️ DWARF 2/3 & Mini Solar Studio and Analyzing

Eine interaktive, mehrsprachige Web-Anwendung auf Basis von **Streamlit**, **Astropy** und **SunPy** zur automatisierten Aufbereitung, Auswertung und astro-metrischen Analyse von Sonnenaufnahmen im FITS-Format (optimiert für DWARF 2/3 Teleskope).

---

## 🚀 Key Features

* **📁 Multi-Quelle FITS-Import:** Direktes Laden über StellarStudio-URLs, Datei-Upload oder lokale Server-Pfade (z. B. Raspberry Pi).
* **🎛️ Bildverarbeitung in Echtzeit:** 
  * Parameter für Helligkeit, Kontrast, Schärfe (Wavelet-Transformation), Belichtung und Sättigung.
  * Automatische Zentrierung und Zuschnitt auf die Sonnenscheibe.
  * Richardson-Lucy Deconvolution zur Detailschärfung.
* **💾 2K Super-Resolution Export:** Exportieren von hochauflösenden (2048x2048) B&W- und Falschfarben-Sonnenbildern.
* **🔬 Astronomische Sonnenfleckenauswertung:**
  * Automatische Korrektur der Bildorientierung (P-Winkel & Parallaktischer Winkel $q$ für Alt-Az / EQ Montierungen).
  * Bestimmung der Relativzahl ($R$), Einzelflecken ($f$) und Gruppen ($g$).
  * Flächenberechnung der Flecken in **MSH** (*Micro-Solar Hemispheres*) mit Korrektur der Randverdunkelung/Projektion.
  * Zuordnung der Fleckengruppen inkl. heliografischer Koordinaten (Breite/Länge).
* **🌐 Mehrsprachigkeit:** Deutsch (🇩🇪), Englisch (🇬🇧), Finnisch (🇫🇮), Griechisch (🇬🇷) und Japanisch (🇯🇵).

---

## 🧪 Validierungs-Fahrplan (SDO Cross-Checking)

Um eine hohe wissenschaftliche Genauigkeit für spätere Langzeitstudien (wie das **Schmetterlingsdiagramm**) zu gewährleisten, durchläuft die Software aktuell eine intensive Validierungsphase:

1. **Globales Test-Grid:** Testen von FITS-Daten aus allen 4 Jahreszeiten von verschiedenen Standorten weltweit.
2. **SDO Overlay-Validation:** Abgleich der berechneten Kippwinkel und Koordinaten gegen **NASA SDO/HMI Continuum** Daten.
3. **Persistenz-Optionen:** Nach Abschluss der Validierung erfolgt die Anbindung an **Google Sheets** sowie die finale Migration auf einen dedizierten **Raspberry Pi 5 Server** für das dauerhafte Daten-Logging.

---

## 🛠️ Installation & Lokaler Start

### Vorraussetzungen
* Python 3.10 oder neuer

### 1. Repository klonen
```bash
git clone [https://github.com/DEIN-BENUTZERNAME/dwarf-solar-studio.git](https://github.com/DEIN-BENUTZERNAME/dwarf-solar-studio.git)
cd dwarf-solar-studio

## Lizenz & Credits
Entwicklung: [Dr. Michael Danielides / Linux1492beta]

Datenreferenzen: SILSO / SIDC Royal Observatory of Belgium (Relativzahlen-Abgleich)

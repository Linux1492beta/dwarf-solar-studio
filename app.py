import csv
from io import BytesIO
import os
from pathlib import Path
import urllib.request
import zoneinfo

from astropy.coordinates import EarthLocation, get_sun
from astropy.io import fits
import astropy.units as u

# Astronomie & Analyse Bibliotheken
from astropy.time import Time
import cv2
import matplotlib.pyplot as plt
import numpy as np
import pywt
import requests
from skimage import restoration
from sklearn.cluster import DBSCAN
import streamlit as st
import sunpy.coordinates.sun as sun
from sunpy.coordinates import HeliographicStonyhurst
import sunpy.map
from timezonefinder import TimezoneFinder

tf = TimezoneFinder()

# Page Config & Styling
st.set_page_config(
    page_title="DWARF 2/3 & Mini Solar Studio and Analyzing",
    page_icon="☀️",
    layout="wide",
)

st.markdown(
    """
<style>
    .main { background-color: #0f172a; color: #f8fafc; }
    div[data-testid="stSidebar"] { background-color: #1e293b; }
    .stApp > header { background-color: transparent; }
    .centered-text { text-align: center; }
</style>
""",
    unsafe_allow_html=True,
)

# ==========================================
# MEHRSPRACHIGKEIT (TRANSLATIONS)
# ==========================================
TRANSLATIONS = {
    "de": {
        "lang_name": "🇩🇪 DE - Deutsch",
        "select_source": "📁 FITS Quelle wählen",
        "import_way": "Import-Weg:",
        "url_link": "StellarStudio Link (URL)",
        "upload_file": "Datei hochladen",
        "server_path": "Server-Pfad (Pi)",
        "load_url_btn": "URL Abrufen & Laden",
        "load_pi_btn": "Vom Pi laden",
        "telescope_settings": "🔭 Teleskop-Einstellungen",
        "mount_mode": "Montierungsmodus für Analyse:",
        "image_adj": "🎛️ Bildanpassung",
        "reset_btn": "🔄 Regler auf Standard zurücksetzen",
        "brightness": "Helligkeit",
        "contrast": "Kontrast",
        "sharpness": "Schärfe",
        "exposure": "Belichtung",
        "saturation": "Sättigung",
        "device": "Aufnahmegerät",
        "date_time": "Datum & Zeit",
        "exp_time": "Belichtung",
        "bw_1to1": "Schwarz-Weiß (Zentriert 1:1)",
        "color_1to1": "Gelb-Orange (Zentriert 1:1)",
        "dl_section": "💾 2K Super-Resolution Download (2048x2048)",
        "dl_bw": "📥 SW 2K-Bild herunterladen",
        "dl_color": "📥 Farbiges 2K-Bild herunterladen",
        "btn_analyze": "🔬 Sonnenbild jetzt analysieren",
        "analyzing_spinner": "Analysiere Flecken auf FITS-Rohdaten & erstelle Karte...",
        "analysis_results": "🔍 Analyse-Ergebnisse",
        "rel_number": "Relativzahl (R)",
        "spots": "Einzelflecken (f)",
        "groups": "Gruppen (g)",
        "area": "Fläche (MSH)",
        "dl_map": "📥 Analyse-Karte herunterladen (PNG)",
        "table_title": "📋 Flecken-Gruppen Übersicht",
        "no_spots": "Keine Fleckengruppen auf der Sonnenoberfläche erkannt.",
        "log_info": "✅ Ergebnisse wurden automatisch in dwarf_sonnen_log.csv protokolliert.",
        "sidebar_info": "👈 Bitte wähle in der Seitenleiste eine FITS-Datei aus (per Link, Upload oder Server-Pfad).",
        "col_group": "Gruppe",
        "col_class": "Klasse",
        "col_lat": "Breite",
        "col_lon": "Länge",
        "col_area": "Fläche (MSH)",
        "col_spots": "Flecken",
        "plot_north": "Sonne Nord Oben",
        "plot_measured": "R_Gemessen",
        "plot_area": "Fläche",
    },
    "en": {
        "lang_name": "🇬🇧 EN - English",
        "select_source": "📁 Select FITS Source",
        "import_way": "Import Method:",
        "url_link": "StellarStudio Link (URL)",
        "upload_file": "Upload File",
        "server_path": "Server Path (Pi)",
        "load_url_btn": "Fetch URL & Load",
        "load_pi_btn": "Load from Pi",
        "telescope_settings": "🔭 Telescope Settings",
        "mount_mode": "Mount Mode for Analysis:",
        "image_adj": "🎛️ Image Adjustment",
        "reset_btn": "🔄 Reset Sliders to Default",
        "brightness": "Brightness",
        "contrast": "Contrast",
        "sharpness": "Sharpness",
        "exposure": "Exposure",
        "saturation": "Saturation",
        "device": "Device",
        "date_time": "Date & Time",
        "exp_time": "Exposure",
        "bw_1to1": "Black & White (Centered 1:1)",
        "color_1to1": "Yellow-Orange (Centered 1:1)",
        "dl_section": "💾 2K Super-Resolution Download (2048x2048)",
        "dl_bw": "📥 Download B&W 2K Image",
        "dl_color": "📥 Download Color 2K Image",
        "btn_analyze": "🔬 Analyze Solar Image Now",
        "analyzing_spinner": "Analyzing spots on FITS raw data & generating map...",
        "analysis_results": "🔍 Analysis Results",
        "rel_number": "Relative Number (R)",
        "spots": "Single Spots (f)",
        "groups": "Groups (g)",
        "area": "Area (MSH)",
        "dl_map": "📥 Download Analysis Map (PNG)",
        "table_title": "📋 Sunspot Groups Overview",
        "no_spots": "No sunspot groups detected on the solar surface.",
        "log_info": "✅ Results automatically logged in dwarf_sonnen_log.csv.",
        "sidebar_info": "👈 Please select a FITS file in the sidebar (via link, upload, or server path).",
        "col_group": "Group",
        "col_class": "Class",
        "col_lat": "Latitude",
        "col_lon": "Longitude",
        "col_area": "Area (MSH)",
        "col_spots": "Spots",
        "plot_north": "Solar North Up",
        "plot_measured": "R_Measured",
        "plot_area": "Area",
    },
    "fi": {
        "lang_name": "🇫🇮 FI - Suomi",
        "select_source": "📁 Valitse FITS-lähde",
        "import_way": "Tuontitapa:",
        "url_link": "StellarStudio-linkki (URL)",
        "upload_file": "Lataa tiedosto",
        "server_path": "Palvelinpolku (Pi)",
        "load_url_btn": "Hae URL & Lataa",
        "load_pi_btn": "Lataa Pi-palvelimelta",
        "telescope_settings": "🔭 Kaukoputken asetukset",
        "mount_mode": "Jalustan tila analyysille:",
        "image_adj": "🎛️ Kuvan säätö",
        "reset_btn": "🔄 Palauta liukusäätimet oletuksiin",
        "brightness": "Kirkkaus",
        "contrast": "Kontrasti",
        "sharpness": "Terävyys",
        "exposure": "Valotus",
        "saturation": "Värikylläisyys",
        "device": "Laite",
        "date_time": "Päiväys & Aika",
        "exp_time": "Valotusaika",
        "bw_1to1": "Mustavalkoinen (Keskitetty 1:1)",
        "color_1to1": "Keltorusehtava (Keskitetty 1:1)",
        "dl_section": "💾 2K Super-Resolution Lataus (2048x2048)",
        "dl_bw": "📥 Lataa MV 2K-kuva",
        "dl_color": "📥 Lataa Väri 2K-kuva",
        "btn_analyze": "🔬 Analysoi aurinkokuva nyt",
        "analyzing_spinner": "Analysoidaan pilkkuja raakatiedoista & luodaan kartta...",
        "analysis_results": "🔍 Analyysin tulokset",
        "rel_number": "Suhteellinen luku (R)",
        "spots": "Yksittäiset pilkut (f)",
        "groups": "Ryhmät (g)",
        "area": "Pinta-ala (MSH)",
        "dl_map": "📥 Lataa analyysikartta (PNG)",
        "table_title": "📋 Auringonpilkkuryhmien yleiskatsaus",
        "no_spots": "Auringon pinnalta ei havaittu pilkkuryhmiä.",
        "log_info": "✅ Tulokset tallennettiin automaattisesti tiedostoon dwarf_sonnen_log.csv.",
        "sidebar_info": "👈 Valitse FITS-tiedosto sivupalkista (linkki, lataus tai palvelinpolku).",
        "col_group": "Ryhmä",
        "col_class": "Luokka",
        "col_lat": "Leveysaste",
        "col_lon": "Pituusaste",
        "col_area": "Pinta-ala (MSH)",
        "col_spots": "Pilkut",
        "plot_north": "Aurinko Pohjoinen Ylhäällä",
        "plot_measured": "R_Mitattu",
        "plot_area": "Pinta-ala",
    },
    "el": {
        "lang_name": "🇬🇷 EL - Ελληνικά",
        "select_source": "📁 Επιλογή πηγής FITS",
        "import_way": "Τρόπος εισαγωγής:",
        "url_link": "Σύνδεσμος StellarStudio (URL)",
        "upload_file": "Μεταφόρτωση αρχείου",
        "server_path": "Διαδρομή διακομιστή (Pi)",
        "load_url_btn": "Ανάκτηση URL & Φόρτωση",
        "load_pi_btn": "Φόρτωση από το Pi",
        "telescope_settings": "🔭 Ρυθμίσεις τηλεσκοπίου",
        "mount_mode": "Λειτουργία στήριξης για ανάλυση:",
        "image_adj": "🎛️ Προσαρμογή εικόνας",
        "reset_btn": "🔄 Επαναφορά ρυθμίσεων",
        "brightness": "Φωτεινότητα",
        "contrast": "Αντίθεση",
        "sharpness": "Οξύτητα",
        "exposure": "Έκθεση",
        "saturation": "Κορεσμός",
        "device": "Συσκευή",
        "date_time": "Ημερομηνία & Ώρα",
        "exp_time": "Έκθεση",
        "bw_1to1": "Ασπρόμαυρο (Κεντραρισμένο 1:1)",
        "color_1to1": "Έγχρωμο (Κεντραρισμένο 1:1)",
        "dl_section": "💾 Λήψη 2K Super-Resolution (2048x2048)",
        "dl_bw": "📥 Λήψη Α/Μ εικόνας 2K",
        "dl_color": "📥 Λήψη έγχρωμης εικόνας 2K",
        "btn_analyze": "🔬 Ανάλυση ηλιακής εικόνας τώρα",
        "analyzing_spinner": "Ανάλυση κηλίδων στα ανεπεξέργαστα δεδομένα & δημιουργία χάρτη...",
        "analysis_results": "🔍 Αποτελέσματα ανάλυσης",
        "rel_number": "Σχετικός αριθμός (R)",
        "spots": "Μεμονωμένες κηλίδες (f)",
        "groups": "Ομάδες (g)",
        "area": "Εμβαδόν (MSH)",
        "dl_map": "📥 Λήψη χάρτη ανάλυσης (PNG)",
        "table_title": "📋 Επισκόπηση ομάδων ηλιακών κηλίδων",
        "no_spots": "Δεν εντοπίστηκαν ομάδες κηλίδων στην ηλιακή επιφάνεια.",
        "log_info": "✅ Τα αποτελέσματα καταγράφηκαν αυτόματα στο dwarf_sonnen_log.csv.",
        "sidebar_info": "👈 Παρακαλώ επιλέξτε ένα αρχείο FITS από τη πλευρική στήλη.",
        "col_group": "Ομάδα",
        "col_class": "Κατηγορία",
        "col_lat": "Πλάτος",
        "col_lon": "Μήκος",
        "col_area": "Εμβαδόν (MSH)",
        "col_spots": "Κηλίδες",
        "plot_north": "Ηλιακός Βορράς Πάνω",
        "plot_measured": "R_Μετρημένο",
        "plot_area": "Εμβαδόν",
    },
    "jp": {
        "lang_name": "🇯🇵 JP - 日本語",
        "select_source": "📁 FITSソースを選択",
        "import_way": "インポート方法:",
        "url_link": "StellarStudio リンク (URL)",
        "upload_file": "ファイルをアップロード",
        "server_path": "サーバーパス (Pi)",
        "load_url_btn": "URLを取得してロード",
        "load_pi_btn": "Piからロード",
        "telescope_settings": "🔭 望遠鏡の設定",
        "mount_mode": "解析用架台モード:",
        "image_adj": "🎛️ 画像調整",
        "reset_btn": "🔄 設定を初期値に戻す",
        "brightness": "明るさ",
        "contrast": "コントラスト",
        "sharpness": "鮮明度",
        "exposure": "露出",
        "saturation": "彩度",
        "device": "撮影機器",
        "date_time": "日時",
        "exp_time": "露出時間",
        "bw_1to1": "モノクロ (中央 1:1)",
        "color_1to1": "カラー (中央 1:1)",
        "dl_section": "💾 2K超解像度ダウンロード (2048x2048)",
        "dl_bw": "📥 2Kモノクロ画像をダウンロード",
        "dl_color": "📥 2Kカラー画像をダウンロード",
        "btn_analyze": "🔬 太陽画像を今すぐ解析",
        "analyzing_spinner": "FITS生データから黒点を解析しマップを作成中...",
        "analysis_results": "🔍 解析結果",
        "rel_number": "相対数 (R)",
        "spots": "単一黒点 (f)",
        "groups": "群数 (g)",
        "area": "面積 (MSH)",
        "dl_map": "📥 解析マップをダウンロード (PNG)",
        "table_title": "📋 太陽黒点群の概要",
        "no_spots": "太陽表面に黒点群は検出されませんでした。",
        "log_info": "✅ 結果は dwarf_sonnen_log.csv に自動記録されました。",
        "sidebar_info": "👈 サイドバーからFITSファイルを選択してください。",
        "col_group": "グループ",
        "col_class": "分類",
        "col_lat": "緯度",
        "col_lon": "経度",
        "col_area": "面積 (MSH)",
        "col_spots": "黒点数",
        "plot_north": "太陽北が上",
        "plot_measured": "測定値 R",
        "plot_area": "面積",
    },
}

# ==========================================
# DEFAULT-WERTE & SESSION STATE
# ==========================================
DEFAULTS = {
    "brightness": 0.0,
    "contrast": 1.0,
    "blend": 0.75,
    "exposure": 0.88,
    "saturation": 1.0,
}

if "lang" not in st.session_state:
    st.session_state.lang = "de"
if "raw_bytes" not in st.session_state:
    st.session_state.raw_bytes = None
if "file_name_stem" not in st.session_state:
    st.session_state.file_name_stem = "Sun_Studio"
if "analysis_results" not in st.session_state:
    st.session_state.analysis_results = None

# Default Werte bei jedem Neustart festlegen
for key, default_val in DEFAULTS.items():
    if key not in st.session_state:
        st.session_state[key] = default_val


def reset_slider_values():
    for key, val in DEFAULTS.items():
        st.session_state[key] = val


def T(key):
    return TRANSLATIONS[st.session_state.lang].get(key, key)


# ==========================================
# SIDEBAR: SPRACHAUSWAHL (GAANZ OBEN)
# ==========================================
st.sidebar.markdown("### 🌐 Language / Sprache")
lang_options = ["de", "en", "fi", "el", "jp"]
selected_lang_code = st.sidebar.selectbox(
    "Select Language:",
    options=lang_options,
    format_func=lambda x: TRANSLATIONS[x]["lang_name"],
    index=lang_options.index(st.session_state.lang),
    label_visibility="collapsed",
)
st.session_state.lang = selected_lang_code

st.sidebar.markdown("---")

# BANNERBILD & TITEL
banner_path = None
for ext in ["banner.png", "banner.jpg", "banner.webp"]:
    p = Path(__file__).parent / ext
    if p.exists():
        banner_path = p
        break

if banner_path:
    st.image(str(banner_path), use_container_width=True)

# KORRIGIERTE TITELÜBERSCHRIFT
st.title("☀️ DWARF 2/3 & Mini Solar Studio and Analyzing")


# ==========================================
# HILFSFUNKTIONEN: BILDVERARBEITUNG
# ==========================================
def crop_to_solar_disk(img, padding_factor=1.05):
    img_uint8 = (img * 255).astype(np.uint8)
    _, thresh = cv2.threshold(img_uint8, 20, 255, cv2.THRESH_BINARY)
    contours, _ = cv2.findContours(
        thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
    )

    h_img, w_img = img.shape[:2]
    if contours:
        c = max(contours, key=cv2.contourArea)
        (x, y), radius = cv2.minEnclosingCircle(c)
        center_x, center_y = int(x), int(y)
        r = int(radius * padding_factor)
    else:
        center_x, center_y = w_img // 2, h_img // 2
        r = min(h_img, w_img) // 2

    x1, x2 = max(0, center_x - r), min(w_img, center_x + r)
    y1, y2 = max(0, center_y - r), min(h_img, center_y + r)
    crop_size = min(x2 - x1, y2 - y1)

    return img[y1 : y1 + crop_size, x1 : x1 + crop_size]


def create_radial_solar_mask(img, core_radius_ratio=0.75, blur_radius=51):
    img_uint8 = (img * 255).astype(np.uint8)
    _, thresh = cv2.threshold(img_uint8, 25, 255, cv2.THRESH_BINARY)
    contours, _ = cv2.findContours(
        thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
    )

    if not contours:
        h, w = img.shape
        center, radius = (w // 2, h // 2), min(h, w) // 2
    else:
        c = max(contours, key=cv2.contourArea)
        (x, y), radius = cv2.minEnclosingCircle(c)
        center, radius = (int(x), int(y)), int(radius)

    h, w = img.shape
    y_grid, x_grid = np.ogrid[:h, :w]
    dist_from_center = np.sqrt((x_grid - center[0]) ** 2 + (y_grid - center[1]) ** 2)
    inner_r, outer_r = radius * core_radius_ratio, radius * 0.98

    mask = np.clip((outer_r - dist_from_center) / (outer_r - inner_r), 0, 1)
    return cv2.GaussianBlur(mask.astype(np.float32), (blur_radius, blur_radius), 0)


def wavelet_sharpen(img, levels=3, weights=[1.6, 1.3, 1.0]):
    coeffs = list(pywt.wavedec2(img, "db1", level=levels))
    for i in range(1, len(coeffs)):
        w = weights[i - 1] if (i - 1) < len(weights) else 1.0
        LH, HL, HH = coeffs[i]
        coeffs[i] = (LH * w, HL * w, HH * w)
    return np.clip(pywt.waverec2(coeffs, "db1"), 0, 1)


def enhance_to_2k(img_array, target_size=2048):
    resized = cv2.resize(
        img_array, (target_size, target_size), interpolation=cv2.INTER_LANCZOS4
    )
    blur = cv2.GaussianBlur(resized, (0, 0), sigmaX=1.5)
    return np.clip(cv2.addWeighted(resized, 1.35, blur, -0.35, 0), 0.0, 1.0)


@st.cache_data(show_spinner=False)
def process_fits_data(fits_bytes_data):
    with fits.open(BytesIO(fits_bytes_data)) as hdul:
        header = hdul[0].header
        data = hdul[0].data.astype(np.float32)

    data = np.squeeze(data)
    if data.ndim == 3:
        data = np.mean(data, axis=0)

    data_norm = (data - np.min(data)) / (np.max(data) - np.min(data))
    cropped = crop_to_solar_disk(data_norm)

    x, y = np.mgrid[-3:4, -3:4]
    g = np.exp(-(x**2 + y**2) / 2.0)
    psf = g / g.sum()

    deconv = restoration.richardson_lucy(cropped, psf, num_iter=20)
    wavelet_sharp = wavelet_sharpen(deconv)

    clahe = cv2.createCLAHE(clipLimit=1.4, tileGridSize=(8, 8))
    enhanced_base = (
        clahe.apply((wavelet_sharp * 255).astype(np.uint8)).astype(np.float32)
        / 255.0
    )
    radial_mask = create_radial_solar_mask(cropped)

    return cropped, enhanced_base, radial_mask, header


# ==========================================
# HILFSFUNKTIONEN: ASTRONOMISCHE ANALYSE
# ==========================================
def hole_sidc_relativzahl(datum):
    ziel_jahr, ziel_monat, ziel_tag = (
        datum.datetime.year,
        datum.datetime.month,
        datum.datetime.day,
    )
    urls = [
        "https://www.sidc.be/SILSO/DATA/EISN/EISN_current.txt",
        "https://www.sidc.be/SILSO/DATA/SN_d_tot_V2.0.txt",
    ]
    for url in urls:
        try:
            req = urllib.request.Request(
                url, headers={"User-Agent": "Mozilla/5.0"}
            )
            with urllib.request.urlopen(req, timeout=5) as response:
                lines = response.read().decode("utf-8").splitlines()
                for line in reversed(lines):
                    parts = line.split()
                    if len(parts) >= 5:
                        j, m, t = (
                            int(parts[0]),
                            int(parts[1]),
                            int(parts[2]),
                        )
                        if j == ziel_jahr and m == ziel_monat and t == ziel_tag:
                            r_val = float(parts[4])
                            return int(r_val) if r_val >= 0 else None
        except Exception:
            continue
    return None


def run_solar_analysis(img_raw_cropped, header, mount_mode="AZ", lang="de"):
    lat_val = header.get("SITELAT", 53.946)
    lon_val = header.get("SITELONG", 13.274)
    beobachtungsort = EarthLocation(
        lat=lat_val * u.deg, lon=lon_val * u.deg, height=50 * u.m
    )

    if "DATE-OBS" in header:
        raw_astropy_time = Time(header["DATE-OBS"])
        tz_name = tf.timezone_at(lng=lon_val, lat=lat_val) or "UTC"
        dt_naive = raw_astropy_time.datetime
        dt_local = dt_naive.replace(tzinfo=zoneinfo.ZoneInfo(tz_name))
        utc_offset_seconds = dt_local.utcoffset().total_seconds()
        aufnahme_zeit = raw_astropy_time - (utc_offset_seconds * u.second)
    else:
        aufnahme_zeit = Time.now()

    data_8u = cv2.normalize(
        img_raw_cropped, None, 0, 255, cv2.NORM_MINMAX, dtype=cv2.CV_8U
    )
    data_8u_flipped = np.flipud(data_8u)

    _, thresh = cv2.threshold(
        data_8u_flipped, 40, 255, cv2.THRESH_BINARY
    )
    contours = cv2.findContours(
        thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
    )[-2]

    if not contours:
        return None, "Error: Solar disk not found."

    groesste_kontur = max(contours, key=cv2.contourArea)
    (zentrum_x, zentrum_y), radius_px = cv2.minEnclosingCircle(groesste_kontur)

    p_winkel = sun.P(aufnahme_zeit)
    if mount_mode == "EQ":
        q_winkel = 0.0 * u.deg
    else:
        sun_pos = get_sun(aufnahme_zeit)
        ha = (
            aufnahme_zeit.sidereal_time("apparent", longitude=beobachtungsort.lon)
            - sun_pos.ra
        )
        dec = sun_pos.dec
        lat = beobachtungsort.lat
        y = np.sin(ha)
        x = np.cos(dec) * np.tan(lat) - np.sin(dec) * np.cos(ha)
        q_winkel = np.arctan2(y, x).to(u.deg)

    astronomischer_winkel = p_winkel + q_winkel

    wahrer_radius_arcsec = sun.angular_radius(aufnahme_zeit).to(u.arcsec).value
    pixel_skala = wahrer_radius_arcsec / radius_px

    meta = {
        "date-obs": aufnahme_zeit.isot,
        "cunit1": "arcsec",
        "cunit2": "arcsec",
        "cdelt1": pixel_skala,
        "cdelt2": pixel_skala,
        "crpix1": zentrum_x + 1,
        "crpix2": zentrum_y + 1,
        "crval1": 0,
        "crval2": 0,
        "crota2": astronomischer_winkel.to(u.deg).value,
        "hglt_obs": sun.B0(aufnahme_zeit).value,
        "hgln_obs": sun.L0(aufnahme_zeit).value,
        "dsun_obs": sun.earth_distance(aufnahme_zeit).to(u.m).value,
        "rsun_obs": wahrer_radius_arcsec,
        "ctype1": "HPLN-TAN",
        "ctype2": "HPLT-TAN",
    }

    sonnen_map = sunpy.map.Map((data_8u_flipped.astype(np.float32), meta))
    rotierte_map = sonnen_map.rotate(order=3)
    rotierte_daten_cv2 = np.ascontiguousarray(
        np.clip(rotierte_map.data, 0, 255).astype(np.uint8)
    )

    zentrum_rot_x = rotierte_map.meta["crpix1"] - 1
    zentrum_rot_y = rotierte_map.meta["crpix2"] - 1

    analyse_maske = np.zeros(rotierte_daten_cv2.shape, dtype=np.uint8)
    cv2.circle(
        analyse_maske,
        (int(zentrum_rot_x), int(zentrum_rot_y)),
        int(radius_px * 0.92),
        255,
        -1,
    )

    flecken_thresh = cv2.adaptiveThreshold(
        rotierte_daten_cv2,
        255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY_INV,
        31,
        7,
    )
    flecken_thresh = cv2.bitwise_and(
        flecken_thresh, flecken_thresh, mask=analyse_maske
    )
    flecken_konturen = cv2.findContours(
        flecken_thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
    )[-2]

    flecken_daten = []
    gesamte_flaeche_msh = 0.0
    hemisphaere_px = 2 * np.pi * (radius_px**2)

    for cnt in flecken_konturen:
        area = cv2.contourArea(cnt)
        if 1 <= area <= 400:
            M = cv2.moments(cnt)
            if M["m00"] != 0:
                cX = int(M["m10"] / M["m00"])
                cY = int(M["m01"] / M["m00"])
                dx, dy = cX - zentrum_rot_x, cY - zentrum_rot_y
                r = np.sqrt(dx**2 + dy**2)
                if r < radius_px:
                    cos_theta = np.sqrt(1 - (r / radius_px) ** 2)
                    if cos_theta > 0.05:
                        korrigierte_flaeche_px = area / cos_theta
                        area_msh = (
                            korrigierte_flaeche_px / hemisphaere_px
                        ) * 1_000_000
                        gesamte_flaeche_msh += area_msh
                        flecken_daten.append(
                            {"x": cX, "y": cY, "area_msh": area_msh}
                        )

    f_count = len(flecken_daten)
    g_count = 0
    gruppen_infos = {}
    labels = []

    if f_count > 0:
        max_dist = radius_px * 0.05
        X = np.array([[d["x"], d["y"]] for d in flecken_daten])
        clustering = DBSCAN(eps=max_dist, min_samples=1).fit(X)
        labels = clustering.labels_
        g_count = len(set(labels))

        for gruppen_id in set(labels):
            indices = np.where(labels == gruppen_id)[0]
            gruppe_flecken = [flecken_daten[i] for i in indices]
            mean_x = np.mean([d["x"] for d in gruppe_flecken])
            mean_y = np.mean([d["y"] for d in gruppe_flecken])

            coord = rotierte_map.pixel_to_world(
                mean_x * u.pix, mean_y * u.pix
            )
            hgs_coord = coord.transform_to(
                HeliographicStonyhurst(obstime=aufnahme_zeit)
            )
            lat_deg = hgs_coord.lat.to(u.deg).value
            lon_deg = hgs_coord.lon.to(u.deg).value

            gruppen_flaeche = sum([d["area_msh"] for d in gruppe_flecken])
            spot_count = len(gruppe_flecken)

            if spot_count == 1:
                klasse = (
                    "A (Pore)"
                    if gruppen_flaeche < 15
                    else "H (Runder Einzelfleck)"
                )
            else:
                if gruppen_flaeche < 20:
                    klasse = "B (Bipolare Poren)"
                elif gruppen_flaeche < 60:
                    klasse = "C (Kleine Gruppe)"
                elif gruppen_flaeche < 150:
                    klasse = "D (Mittlere Gruppe)"
                else:
                    klasse = "E/F (Groß & Komplex)"

            gruppen_infos[gruppen_id] = {
                "lat": lat_deg,
                "lon": lon_deg,
                "area": gruppen_flaeche,
                "klasse": klasse,
                "spot_count": spot_count,
            }

    R_relativ = (10 * g_count) + f_count
    r_sidc = hole_sidc_relativzahl(aufnahme_zeit)

    # Matplotlib Figure generieren (Dynamische Übersetzung)
    fig = plt.figure(figsize=(8, 8))
    ax = fig.add_subplot(111, projection=rotierte_map)
    ax.set_facecolor("black")
    rotierte_map.plot(axes=ax, cmap="gray", vmin=0, vmax=255)
    rotierte_map.draw_grid(
        axes=ax, color="cyan", alpha=0.4, linewidth=0.8, grid_spacing=15 * u.deg
    )
    rotierte_map.draw_limb(axes=ax, color="yellow", alpha=0.6, linewidth=1.0)

    farben = plt.colormaps["tab10"]
    for idx, d in enumerate(flecken_daten):
        g_id = labels[idx] if len(labels) > 0 else 0
        ax.plot(
            d["x"],
            d["y"],
            "o",
            markeredgecolor=farben(g_id % 10),
            markerfacecolor="none",
            markersize=10,
            markeredgewidth=1.8,
            transform=ax.get_transform("pixel"),
        )

    rand_arcsec = 1100
    delta_px = rand_arcsec / pixel_skala
    ax.set_xlim(zentrum_rot_x - delta_px, zentrum_rot_x + delta_px)
    ax.set_ylim(zentrum_rot_y - delta_px, zentrum_rot_y + delta_px)

    sidc_str = f" | R_SIDC={r_sidc}" if r_sidc is not None else ""
    t_north = TRANSLATIONS[lang]["plot_north"]
    t_meas = TRANSLATIONS[lang]["plot_measured"]
    t_area = TRANSLATIONS[lang]["plot_area"]

    ax.set_title(
        f"{t_north} | {aufnahme_zeit.strftime('%Y-%m-%d %H:%M')} UTC\n"
        f"{t_meas}={R_relativ:.0f} (g={g_count}, f={f_count}){sidc_str} | {t_area}: {gesamte_flaeche_msh:.0f} MSH",
        pad=15,
        fontsize=10,
    )

    # CSV Logging
    csv_pfad = "dwarf_sonnen_log.csv"
    datei_existiert = os.path.isfile(csv_pfad)
    existing_keys = set()
    if datei_existiert:
        with open(csv_pfad, mode="r", encoding="utf-8") as f_read:
            reader = csv.reader(f_read, delimiter=";")
            next(reader, None)
            for row in reader:
                if len(row) >= 7:
                    existing_keys.add((row[0], row[1], row[6]))

    datum_str = aufnahme_zeit.strftime("%Y-%m-%d")
    zeit_str = aufnahme_zeit.strftime("%H:%M:%S")

    with open(csv_pfad, mode="a", newline="", encoding="utf-8") as f_write:
        writer = csv.writer(f_write, delimiter=";")
        if not datei_existiert:
            writer.writerow([
                "Datum",
                "Uhrzeit_UTC",
                "R_gesamt",
                "f_gesamt",
                "g_gesamt",
                "Gesamtflaeche_MSH",
                "Gruppen_ID",
                "Klasse",
                "Breite_deg",
                "Laenge_deg",
                "Gruppenflaeche_MSH",
                "Flecken_in_Gruppe",
            ])

        if g_count > 0:
            for gid, info in gruppen_infos.items():
                if (datum_str, zeit_str, str(gid)) not in existing_keys:
                    writer.writerow([
                        datum_str,
                        zeit_str,
                        int(R_relativ),
                        f_count,
                        g_count,
                        round(gesamte_flaeche_msh, 1),
                        gid,
                        info["klasse"][:1],
                        round(info["lat"], 1),
                        round(info["lon"], 1),
                        round(info["area"], 1),
                        info["spot_count"],
                    ])
        else:
            if (datum_str, zeit_str, "-") not in existing_keys:
                writer.writerow([
                    datum_str,
                    zeit_str,
                    0,
                    0,
                    0,
                    0.0,
                    "-",
                    "-",
                    "",
                    "",
                    0.0,
                    0,
                ])

    results = {
        "fig": fig,
        "R": R_relativ,
        "f": f_count,
        "g": g_count,
        "flaeche": gesamte_flaeche_msh,
        "r_sidc": r_sidc,
        "gruppen": gruppen_infos,
        "zeit": aufnahme_zeit.strftime("%Y-%m-%d %H:%M UTC"),
    }
    return results, None


# ==========================================
# SIDEBAR / INPUT-METHODEN
# ==========================================
st.sidebar.header(T("select_source"))
import_option = st.sidebar.radio(
    T("import_way"),
    [T("url_link"), T("upload_file"), T("server_path")],
)

if import_option == T("url_link"):
    url = st.sidebar.text_input(
        "StellarStudio FITS URL:", placeholder="https://.../DWARF3_Sun.fits"
    )
    if url and st.sidebar.button(T("load_url_btn")):
        with st.spinner("..."):
            r = requests.get(url)
            if r.status_code == 200:
                st.session_state.raw_bytes = r.content
                st.session_state.file_name_stem = Path(url).stem
                st.session_state.analysis_results = None
                st.sidebar.success("OK!")

elif import_option == T("upload_file"):
    uploaded = st.sidebar.file_uploader(
        "FITS", type=["fits", "fit"], label_visibility="collapsed"
    )
    if uploaded:
        st.session_state.raw_bytes = uploaded.read()
        st.session_state.file_name_stem = Path(uploaded.name).stem
        st.session_state.analysis_results = None

elif import_option == T("server_path"):
    server_path_str = st.sidebar.text_input(
        "Path:", "/home/pi/dwarf3_data/Sun.fits"
    )
    if Path(server_path_str).exists() and st.sidebar.button(T("load_pi_btn")):
        with open(server_path_str, "rb") as f:
            st.session_state.raw_bytes = f.read()
        st.session_state.file_name_stem = Path(server_path_str).stem
        st.session_state.analysis_results = None
        st.sidebar.success("OK!")

st.sidebar.markdown("---")
st.sidebar.subheader(T("telescope_settings"))
mount_mode = st.sidebar.selectbox(
    T("mount_mode"),
    ["AZ (Alt-Azimutal)", "EQ (Parallaktisch)"],
)
selected_mount = "EQ" if "EQ" in mount_mode else "AZ"

# ==========================================
# VERARBEITUNG & DISPLAY
# ==========================================
if st.session_state.raw_bytes is not None:
    cropped_base, enhanced_base, radial_mask, header = process_fits_data(
        st.session_state.raw_bytes
    )

    st.sidebar.markdown("---")
    st.sidebar.subheader(T("image_adj"))

    st.sidebar.button(
        T("reset_btn"),
        on_click=reset_slider_values,
        use_container_width=True,
    )

    brightness = st.sidebar.slider(
        f"{T('brightness')} (Std: {DEFAULTS['brightness']:.2f})",
        -0.3,
        0.3,
        key="brightness",
        step=0.01,
    )
    contrast = st.sidebar.slider(
        f"{T('contrast')} (Std: {DEFAULTS['contrast']:.2f})",
        0.5,
        2.0,
        key="contrast",
        step=0.05,
    )
    blend = st.sidebar.slider(
        f"{T('sharpness')} (Std: {DEFAULTS['blend']:.2f})",
        0.0,
        1.0,
        key="blend",
        step=0.05,
    )
    exposure = st.sidebar.slider(
        f"{T('exposure')} (Std: {DEFAULTS['exposure']:.2f})",
        0.5,
        1.2,
        key="exposure",
        step=0.02,
    )
    saturation = st.sidebar.slider(
        f"{T('saturation')} (Std: {DEFAULTS['saturation']:.2f})",
        0.2,
        1.8,
        key="saturation",
        step=0.05,
    )

    sharpened_full = blend * enhanced_base + (1.0 - blend) * cropped_base
    base_bw = radial_mask * sharpened_full + (1.0 - radial_mask) * cropped_base

    img_adj = np.clip((base_bw - 0.5) * contrast + 0.5 + brightness, 0, 1)
    img_damped = np.clip(img_adj * exposure, 0, 1)

    rgb = np.zeros((*base_bw.shape, 3), dtype=np.float32)
    rgb[:, :, 0] = np.clip(
        np.power(img_damped, 0.95) * (1.1 * saturation), 0, 1
    )
    rgb[:, :, 1] = np.clip(
        np.power(img_damped, 1.15) * (0.70 * saturation), 0, 1
    )
    rgb[:, :, 2] = np.clip(img_damped * 0.05, 0, 1)

    # HEADER INFORMATIONEN
    telescope_device = header.get(
        "TELESCOP", header.get("INSTRUME", "DWARF Teleskop")
    )
    raw_date = str(header.get("DATE-OBS", "N/A"))
    if "T" in raw_date:
        d_part, t_part = raw_date.split("T")
        date_str = f"{d_part} {t_part.replace('Z', '')} UTC"
    else:
        date_str = f"{raw_date} UTC" if raw_date != "N/A" else "N/A"
    exp = header.get("EXPOSURE", header.get("EXPTIME", "N/A"))

    st.info(
        f"📷 **{T('device')}:** {telescope_device} | 🕒 **{T('date_time')}:** {date_str} | ⏱️ **{T('exp_time')}:** {exp}s"
    )

    col1, col2 = st.columns(2)
    with col1:
        st.subheader(T("bw_1to1"))
        st.image(img_adj, use_container_width=True, clamp=True)

    with col2:
        st.subheader(T("color_1to1"))
        st.image(rgb, use_container_width=True, clamp=True)

    # 2K Download Section
    st.markdown("---")
    st.subheader(T("dl_section"))

    col_btn1, col_btn2 = st.columns(2)

    bw_2k = (enhance_to_2k(img_adj) * 255).astype(np.uint8)
    _, bw_encoded = cv2.imencode(".png", bw_2k)
    col_btn1.download_button(
        label=T("dl_bw"),
        data=bw_encoded.tobytes(),
        file_name=f"{st.session_state.file_name_stem}_SW.png",
        mime="image/png",
    )

    col_2k = (enhance_to_2k(rgb) * 255).astype(np.uint8)
    col_2k_bgr = cv2.cvtColor(col_2k, cv2.COLOR_RGB2BGR)
    _, col_encoded = cv2.imencode(".png", col_2k_bgr)
    col_btn2.download_button(
        label=T("dl_color"),
        data=col_encoded.tobytes(),
        file_name=f"{st.session_state.file_name_stem}_Farbe.png",
        mime="image/png",
    )

    # ==========================================
    # ANALYSE BUTTON (Zentriert)
    # ==========================================
    st.markdown("---")
    col_l, col_btn_center, col_r = st.columns([1, 2, 1])
    if col_btn_center.button(
        T("btn_analyze"),
        type="primary",
        use_container_width=True,
    ):
        with st.spinner(T("analyzing_spinner")):
            res, err = run_solar_analysis(
                cropped_base,
                header,
                mount_mode=selected_mount,
                lang=st.session_state.lang,
            )
            if err:
                st.error(err)
            else:
                st.session_state.analysis_results = res
                st.success("OK!")

    # ANALYSE ERGEBNISSE ANZEIGEN
    if st.session_state.analysis_results is not None:
        res = st.session_state.analysis_results
        st.markdown(
            f"<h2 class='centered-text'>{T('analysis_results')}</h2>",
            unsafe_allow_html=True,
        )

        m1, m2, m3, m4 = st.columns(4)
        m1.metric(T("rel_number"), f"{res['R']:.0f}")
        m2.metric(T("spots"), res["f"])
        m3.metric(T("groups"), res["g"])
        sidc_display = (
            f"{res['r_sidc']}" if res["r_sidc"] is not None else "N/A"
        )
        m4.metric(
            T("area"),
            f"{res['flaeche']:.0f}",
            delta=f"SIDC R: {sidc_display}",
        )

        st.markdown("<br>", unsafe_allow_html=True)

        # 1. ANALYSE-BILD MITTIG
        c_left, c_img, c_right = st.columns([0.15, 0.7, 0.15])
        with c_img:
            st.pyplot(res["fig"], use_container_width=True)

            buf = BytesIO()
            res["fig"].savefig(buf, format="png", dpi=300, bbox_inches="tight")
            st.download_button(
                label=T("dl_map"),
                data=buf.getvalue(),
                file_name=f"{st.session_state.file_name_stem}_Analyse.png",
                mime="image/png",
                use_container_width=True,
            )

        st.markdown("<br><hr><br>", unsafe_allow_html=True)

        # 2. FLECKENAUSWERTUNGSTABELLE DARUNTER (MITTIG)
        st.markdown(
            f"<h3 class='centered-text'>{T('table_title')}</h3>",
            unsafe_allow_html=True,
        )

        t_left, t_center, t_right = st.columns([0.1, 0.8, 0.1])
        with t_center:
            if res["gruppen"]:
                table_data = []
                for gid, info in res["gruppen"].items():
                    table_data.append({
                        T("col_group"): f"#{gid}",
                        T("col_class"): info["klasse"],
                        T("col_lat"): f"{info['lat']:>5.1f}°",
                        T("col_lon"): f"{info['lon']:>5.1f}°",
                        T("col_area"): f"{info['area']:.1f}",
                        T("col_spots"): info["spot_count"],
                    })
                st.dataframe(
                    table_data, use_container_width=True, hide_index=True
                )
            else:
                st.info(T("no_spots"))

        st.markdown(
            f"<p class='centered-text'>{T('log_info')}</p>",
            unsafe_allow_html=True,
        )

else:
    st.info(T("sidebar_info"))
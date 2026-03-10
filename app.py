import streamlit as st
import json
from fpdf import FPDF
import io

# --- KONFIGURACJA STRONY ---
st.set_page_config(page_title="Kalkulator Masarski Pro", page_icon="🍖", layout="centered")

# Domyślna baza przepisów (na 1kg mięsa)
DEFAULT_RECIPES = [
    {
        "nazwa": "Kiełbasa Swojska",
        "opis": "Klasyczna wiejska kiełbasa z wyraźnym czosnkiem i majerankiem.",
        "proporcje_miesa": {"Klasa I (szynka/schab)": 0.6, "Klasa II (boczek/podgardle)": 0.3, "Klasa III (golonka/kleiste)": 0.1},
        "przyprawy": {
            "Sól / Peklosól (g)": 18,
            "Pieprz czarny (g)": 2,
            "Czosnek świeży (g)": 3,
            "Majeranek (g)": 1,
            "Woda (ml)": 50
        },
        "instrukcja": "1. Mięso pokroić w kostkę.\n2. Peklować 24-48h w lodówce.\n3. Zmielić: Klasa I (12mm), Klasa II (8mm), Klasa III (2-3mm).\n4. Wymieszać wszystko z przyprawami do kleistości.\n5. Nadziać jelita, osadzać 2h i wędzić ok. 3h dymem 55-60st."
    },
    {
        "nazwa": "Biała Kiełbasa Parzona",
        "opis": "Delikatna kiełbasa idealna do żurku lub z grilla.",
        "proporcje_miesa": {"Klasa I (wieprzowina chuda)": 0.5, "Klasa II (łopatka/boczek)": 0.4, "Klasa III (wołowe lub golonka)": 0.1},
        "przyprawy": {
            "Sól niejodowana (g)": 18,
            "Pieprz biały (g)": 1.5,
            "Majeranek (g)": 4,
            "Czosnek (g)": 3,
            "Gorczyca (g)": 1
        },
        "instrukcja": "1. Mięso schłodzić przed mieleniem.\n2. Zmielić klasy mięsa wg preferencji (zalecane średnie oczka).\n3. Dodać przyprawy i wyrabiać z zimną wodą.\n4. Parzyć w wodzie o temp. 80°C przez ok. 20-25 minut (do 68°C w środku)."
    }
]

# --- FUNKCJE ---

def clean_polish_chars(text):
    """Zastępuje polskie znaki diakrytyczne dla standardowych czcionek PDF"""
    chars = {"ą":"a", "ć":"c", "ę":"e", "ł":"l", "ń":"n", "ó":"o", "ś":"s", "ź":"z", "ż":"z",
             "Ą":"A", "Ć":"C", "Ę":"E", "Ł":"L", "Ń":"N", "Ó":"O", "Ś":"S", "Ź":"Z", "Ż":"Z"}
    for k, v in chars.items():
        text = text.replace(k, v)
    return text

def generate_pdf(recipe, weight, calculated_spices):
    """Generuje dokument PDF i zwraca go jako obiekt typu bytes"""
    pdf = FPDF()
    pdf.add_page()
    
    # Nagłówek
    pdf.set_font("Helvetica", "B", 16)
    pdf.cell(0, 10, clean_polish_chars(f"Receptura: {recipe['nazwa']}"), new_x="LMARGIN", new_y="NEXT", align="C")
    pdf.set_font("Helvetica", "", 12)
    pdf.cell(0, 10, f"Waga surowca: {weight} kg", new_x="LMARGIN", new_y="NEXT", align="C")
    pdf.ln(10)
    
    # Składniki mięsne
    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(0, 10, "Skladniki miesne:", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", "", 11)
    for m, p in recipe['proporcje_miesa'].items():
        pdf.cell(0, 8, clean_polish_chars(f"- {m}: {round(p * weight, 2)} kg"), new_x="LMARGIN", new_y="NEXT")
    
    pdf.ln(5)
    
    # Przyprawy
    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(0, 10, "Dodatki i przyprawy:", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", "", 11)
    for s_name, s_val in calculated_spices.items():
        pdf.cell(0, 8, clean_polish_chars(f"- {s_name}: {s_val}"), new_x="LMARGIN", new_y="NEXT")
        
    pdf.ln(10)
    
    # Instrukcja
    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(0, 10, "Instrukcja wykonania:", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", "", 10)
    pdf.multi_cell(0, 7, clean_polish_chars(recipe['instrukcja']))
    
    # KLUCZOWA ZMIANA: Konwersja bytearray na bytes
    return bytes(pdf.output())

# --- INTERFEJS UŻYTKOWNIKA ---

st.title("🍖 Kalkulator Receptur Masarskich")

# Główna sekcja wprowadzania danych
st.subheader("1. Podstawowe informacje")
meat_weight = st.number_input("Ile kg mięsa łącznie przygotowałeś?", min_value=0.1, value=5.0, step=0.1, help="Wpisz wagę całego surowca, który masz na stole.")

recipe_names = [r['nazwa'] for r in DEFAULT_RECIPES]
selected_name = st.selectbox("2. Wybierz rodzaj wyrobu:", recipe_names)
recipe = next(r for r in DEFAULT_RECIPES if r['nazwa'] == selected_name)

st.divider()

# Wyświetlanie wyników w kolumnach
st.subheader(f"Obliczenia dla: {selected_name} ({meat_weight} kg)")

col1, col2 = st.columns(2)

with col1:
    st.markdown("### 🛒 Surowiec")
    for m_class, m_ratio in recipe['proporcje_miesa'].items():
        total_m = round(m_ratio * meat_weight, 2)
        st.write(f"**{m_class}:** {total_m} kg")

with col2:
    st.markdown("### 🧂 Przyprawy")
    calculated_spices = {}
    for s_name, s_amount in recipe['przyprawy'].items():
        total_s = round(s_amount * meat_weight, 2)
        unit = "g" if "ml" not in s_name.lower() else "ml"
        display_val = f"{total_s} {unit}"
        calculated_spices[s_name] = display_val
        st.write(f"**{s_name}:** {display_val}")

st.info(f"📝 **Instrukcja:** {recipe['instrukcja']}")

st.divider()

# Sekcja pobierania
try:
    # Generujemy PDF
    pdf_data = generate_pdf(recipe, meat_weight, calculated_spices)
    
    st.download_button(
        label="📥 Pobierz przepis jako PDF",
        data=pdf_data,
        file_name=f"przepis_{selected_name.replace(' ', '_')}.pdf",
        mime="application/pdf",
        use_container_width=True
    )
except Exception as e:
    st.error(f"Wystąpił nieoczekiwany błąd podczas przygotowywania pliku: {e}")

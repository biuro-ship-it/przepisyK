import streamlit as st
import json
from fpdf import FPDF
import io

# --- KONFIGURACJA ---
st.set_page_config(page_title="Kalkulator Masarski Pro", page_icon="🍖", layout="wide")

# Domyślne przepisy (na 1kg mięsa)
DEFAULT_RECIPES = [
    {
        "nazwa": "Kiełbasa Swojska",
        "opis": "Klasyczna wiejska kiełbasa z wyraźnym czosnkiem.",
        "proporcje_miesa": {"Klasa I (chude)": 0.6, "Klasa II (tłustsze)": 0.3, "Klasa III (kleiste)": 0.1},
        "przyprawy": {
            "Sól / Peklosól (g)": 18,
            "Pieprz czarny (g)": 2,
            "Czosnek świeży (g)": 3,
            "Majeranek (g)": 1,
            "Woda (ml)": 50
        },
        "instrukcja": "1. Mięso pokroić w kostkę 3-5cm.\n2. Peklować 24-48h w temp. 4-6°C.\n3. Klasę I zmielić na szarpaku, Klasę II na 8mm, Klasę III na 3mm.\n4. Wyrabiać do uzyskania odpowiedniej kleistości.\n5. Nadziewać jelita wieprzowe 28/32mm.\n6. Osadzać 2h, wędzić do koloru (ok. 3h), parzyć do 68°C wewnątrz."
    },
    {
        "nazwa": "Kiełbasa Krakowska Parzona",
        "opis": "Gruba kiełbasa kanapkowa o zdecydowanym smaku.",
        "proporcje_miesa": {"Klasa I (szynka/schab)": 0.8, "Klasa III (wołowe/golonka)": 0.2},
        "przyprawy": {
            "Peklosól (g)": 19,
            "Pieprz biały (g)": 1.5,
            "Gałka muszkatołowa (g)": 0.5,
            "Kolendra mielona (g)": 0.3,
            "Czosnek (g)": 1.5
        },
        "instrukcja": "1. Mięso klasy I pokroić w dużą kostkę, klasę III mocno schłodzić i zmielić dwukrotnie na najdrobniejszym sitku.\n2. Wymieszać przyprawy z mięsem klasy III i wodą (ok. 5%).\n3. Połączyć z kawałkami klasy I, wyrabiać aż masa zacznie mocno kleić.\n4. Napełniać osłonki białkowe 65mm.\n5. Wędzić gorącym dymem, parzyć w 80°C do osiągnięcia 68°C w środku."
    }
]

# --- FUNKCJE POMOCNICZE ---

def clean_polish_chars(text):
    """Prosta funkcja czyszcząca znaki diakrytyczne dla standardowych czcionek PDF"""
    chars = {"ą":"a", "ć":"c", "ę":"e", "ł":"l", "ń":"n", "ó":"o", "ś":"s", "ź":"z", "ż":"z",
             "Ą":"A", "Ć":"C", "Ę":"E", "Ł":"L", "Ń":"N", "Ó":"O", "Ś":"S", "Ź":"Z", "Ż":"Z"}
    for k, v in chars.items():
        text = text.replace(k, v)
    return text

def generate_pdf(recipe, weight, calculated_spices):
    pdf = FPDF()
    pdf.add_page()
    
    # Nagłówek
    pdf.set_font("Helvetica", "B", 16)
    pdf.cell(0, 10, clean_polish_chars(f"Receptura: {recipe['nazwa']}"), ln=True, align="C")
    pdf.set_font("Helvetica", "", 12)
    pdf.cell(0, 10, f"Data: 2024-05-20 | Ilosc miesa: {weight} kg", ln=True, align="C")
    pdf.ln(10)
    
    # Składniki
    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(0, 10, "Skladniki i przyprawy:", ln=True)
    pdf.set_font("Helvetica", "", 11)
    
    # Mięso
    for m, p in recipe['proporcje_miesa'].items():
        pdf.cell(0, 8, clean_polish_chars(f"- {m}: {round(p * weight, 2)} kg"), ln=True)
    
    pdf.ln(5)
    # Przyprawy
    for s_name, s_val in calculated_spices.items():
        pdf.cell(0, 8, clean_polish_chars(f"- {s_name}: {s_val}"), ln=True)
        
    pdf.ln(10)
    # Instrukcja
    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(0, 10, "Instrukcja wykonania:", ln=True)
    pdf.set_font("Helvetica", "", 10)
    pdf.multi_cell(0, 8, clean_polish_chars(recipe['instrukcja']))
    
    return pdf.output()

# --- INTERFEJS ---

st.sidebar.header("⚙️ Ustawienia Bazowe")
meat_weight = st.sidebar.number_input("Łączna masa mięsa (kg)", min_value=0.1, value=5.0, step=0.5)

st.title("🍖 Kalkulator Receptur Masarskich Pro")
st.markdown(f"Aktualnie obliczasz proporcje dla: **{meat_weight} kg** surowca.")

# Wybór przepisu
recipe_names = [r['nazwa'] for r in DEFAULT_RECIPES]
selected_name = st.selectbox("Wybierz rodzaj wyrobu:", recipe_names)
recipe = next(r for r in DEFAULT_RECIPES if r['nazwa'] == selected_name)

st.info(f"💡 **Opis:** {recipe['opis']}")

col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("🛒 Skład mięsny")
    meat_data = []
    for m_class, m_ratio in recipe['proporcje_miesa'].items():
        total_m = round(m_ratio * meat_weight, 2)
        meat_data.append({"Klasa": m_class, "Ilość (kg)": total_m})
        st.metric(label=m_class, value=f"{total_m} kg")
    
    st.table(meat_data)

with col2:
    st.subheader("🧂 Przyprawy i dodatki")
    spices_results = {}
    spices_table = []
    
    for s_name, s_amount in recipe['przyprawy'].items():
        total_s = round(s_amount * meat_weight, 2)
        unit = "g" if "ml" not in s_name.lower() else "ml"
        spices_results[s_name] = f"{total_s} {unit}"
        spices_table.append({"Dodatek": s_name, "Waga/Ilość": f"{total_s} {unit}"})
    
    st.table(spices_table)

# Instrukcja
with st.expander("📝 Pełna instrukcja technologiczna", expanded=True):
    st.write(recipe['instrukcja'])

# Generowanie PDF
st.divider()
try:
    pdf_bytes = generate_pdf(recipe, meat_weight, spices_results)
    st.download_button(
        label="📥 Pobierz Kartę Technologiczną (PDF)",
        data=pdf_bytes,
        file_name=f"przepis_{selected_name.replace(' ', '_')}.pdf",
        mime="application/pdf",
        use_container_width=True
    )
except Exception as e:
    st.error(f"Błąd podczas generowania PDF: {e}")

st.caption("Aplikacja wspiera procesy rzemieślnicze. Pamiętaj o zachowaniu higieny i temperatur podczas produkcji!")

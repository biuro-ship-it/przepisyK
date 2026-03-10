import streamlit as st
import json
from fpdf import FPDF

# Konfiguracja strony
st.set_page_config(page_title="Kalkulator Masarski", page_icon="🍖")

# Funkcja do wczytywania bazy danych
def load_recipes():
    with open('recipes.json', 'r', encoding='utf-8') as f:
        return json.load(f)

# Funkcja generująca PDF
def create_pdf(nazwa, waga, przyprawy, instrukcja):
    pdf = FPDF()
    pdf.add_page()
    pdf.add_font('DejaVu', '', 'DejaVuSans.ttf', unicode=True) # Wymaga pliku czcionki dla polskic znaków
    pdf.set_font('Arial', 'B', 16)
    pdf.cell(200, 10, txt=f"Receptura: {nazwa}", ln=True, align='C')
    pdf.set_font('Arial', '', 12)
    pdf.cell(200, 10, txt=f"Ilość mięsa: {waga} kg", ln=True)
    pdf.ln(10)
    pdf.cell(200, 10, txt="Potrzebne przyprawy:", ln=True)
    for p, ilosc in przyprawy.items():
        pdf.cell(200, 8, txt=f"- {p}: {round(ilosc * waga, 2)}", ln=True)
    pdf.ln(10)
    pdf.multi_cell(0, 10, txt=f"Instrukcja:\n{instrukcja}")
    return pdf.output(dest='S').encode('latin-1', errors='replace') # Uproszczone na start

# --- INTERFEJS ---
st.title("🍖 Kalkulator Receptur Masarskich")

recipes = load_recipes()
recipe_names = [r['nazwa'] for r in recipes]

# 1. Podaj ilość mięsa
meat_weight = st.number_input("Ile kg mięsa przygotowałeś?", min_value=0.1, value=1.0, step=0.1)

# 2. Wybierz kiełbasę
selected_recipe_name = st.selectbox("Wybierz rodzaj kiełbasy:", recipe_names)
selected_recipe = next(r for r in recipes if r['nazwa'] == selected_recipe_name)

# 3. Przycisk oblicz
if st.button("Oblicz ilość potrzebnych przypraw"):
    st.subheader(f"Składniki na {meat_weight} kg mięsa:")
    
    # Wyświetlanie przypraw w tabeli
    calculated_spices = []
    for przyprawa, ilosc in selected_recipe['przyprawy'].items():
        calculated_spices.append({
            "Przyprawa": przyprawa,
            "Ilość łączna": f"{round(ilosc * meat_weight, 2)}"
        })
    
    st.table(calculated_spices)
    
    st.info("**Instrukcja wykonania:**")
    st.write(selected_recipe['instrukcja'])

    # Opcja pobrania PDF (zamiast wysyłki, co jest łatwiejsze na start)
    st.download_button(
        label="Pobierz przepis jako PDF",
        data="Tu byłby PDF (wymaga konfiguracji czcionek)",
        file_name=f"przepis_{selected_recipe_name}.txt",
        mime="text/plain"
    )

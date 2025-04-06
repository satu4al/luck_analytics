import streamlit as st
from datetime import datetime
import pyswisseph as swe
from fpdf import FPDF
import tempfile
import os

# Set ephemeris path
swe.set_ephe_path('')

# Vimshottari Dasha Data
DASHA_YEARS = {
    'Ketu': 7, 'Venus': 20, 'Sun': 6, 'Moon': 10, 'Mars': 7,
    'Rahu': 18, 'Jupiter': 16, 'Saturn': 19, 'Mercury': 17
}
DASHA_SEQUENCE = ['Ketu', 'Venus', 'Sun', 'Moon', 'Mars', 'Rahu', 'Jupiter', 'Saturn', 'Mercury']
NAKSHATRA_LORDS = [
    ('Ketu', 0), ('Venus', 13.2), ('Sun', 26.4), ('Moon', 39.6),
    ('Mars', 52.8), ('Rahu', 66.0), ('Jupiter', 79.2),
    ('Saturn', 92.4), ('Mercury', 105.6), ('Ketu', 118.8),
    ('Venus', 132.0), ('Sun', 145.2), ('Moon', 158.4),
    ('Mars', 171.6), ('Rahu', 184.8), ('Jupiter', 198.0),
    ('Saturn', 211.2), ('Mercury', 224.4), ('Ketu', 237.6),
    ('Venus', 250.8), ('Sun', 264.0), ('Moon', 277.2),
    ('Mars', 290.4), ('Rahu', 303.6), ('Jupiter', 316.8),
    ('Saturn', 330.0), ('Mercury', 343.2)
]

DASHA_PREDICTIONS = {
    'Sun': ("Leadership in career", "Clarity in love", "Watch your blood pressure"),
    'Moon': ("Creative career choices", "Emotional bonding", "Good emotional health"),
    'Mars': ("Action-oriented projects", "Conflicts possible", "Injury-prone period"),
    'Mercury': ("Learning and growth", "Smart communication", "Mental rest needed"),
    'Jupiter': ("Expansion & blessings", "Marriage potential", "Spiritual wellness"),
    'Venus': ("Career in arts/beauty", "Strong love life", "Reproductive health"),
    'Saturn': ("Slow but steady success", "Karmic love lessons", "Bone & joint care"),
    'Rahu': ("Sudden career rise", "Unconventional romance", "Mental health focus"),
    'Ketu': ("Letting go phase", "Detached from love", "Spiritual health focus"),
}

def get_moon_lord(moon_deg):
    for i, (_, start_deg) in enumerate(NAKSHATRA_LORDS):
        if moon_deg < start_deg:
            return NAKSHATRA_LORDS[i - 1][0]
    return NAKSHATRA_LORDS[-1][0]

def calculate_dasha_start(birth_year, moon_deg):
    lord = get_moon_lord(moon_deg)
    idx = DASHA_SEQUENCE.index(lord)
    start_year = birth_year
    dasha_list = []
    
    for i in range(len(DASHA_SEQUENCE)):
        lord = DASHA_SEQUENCE[(idx + i) % len(DASHA_SEQUENCE)]
        duration = DASHA_YEARS[lord]
        dasha_list.append((lord, round(start_year), round(start_year + duration)))
        start_year += duration
    return dasha_list

def generate_pdf(name, dob, latitude, longitude, moon_lord, current_dasha, career, love, health, dasha_periods):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=14)

    pdf.cell(200, 10, txt="🔮 Vedic Astrology Dasha Report", ln=1, align="C")
    pdf.ln(5)
    pdf.set_font("Arial", size=12)

    pdf.cell(200, 10, txt=f"Name: {name}", ln=True)
    pdf.cell(200, 10, txt=f"Date of Birth: {dob.strftime('%d %B %Y %H:%M')}", ln=True)
    pdf.cell(200, 10, txt=f"Location: Lat {latitude}, Lon {longitude}", ln=True)
    pdf.ln(5)

    pdf.set_font("Arial", 'B', size=12)
    pdf.cell(200, 10, txt=f"Moon Nakshatra Lord: {moon_lord}", ln=True)
    pdf.cell(200, 10, txt=f"Current Mahadasha: {current_dasha[0]} ({current_dasha[1]} - {current_dasha[2]})", ln=True)
    pdf.ln(5)

    pdf.set_font("Arial", size=12)
    pdf.multi_cell(0, 10, f"💼 Career: {career}")
    pdf.multi_cell(0, 10, f"❤️ Love: {love}")
    pdf.multi_cell(0, 10, f"🧘 Health: {health}")
    pdf.ln(5)

    pdf.set_font("Arial", 'B', 12)
    pdf.cell(200, 10, txt="Full Vimshottari Dasha Periods", ln=True)
    pdf.set_font("Arial", size=11)
    for lord, start, end in dasha_periods:
        pdf.cell(200, 8, txt=f"{lord}: {start} - {end}", ln=True)

    tmp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
    pdf.output(tmp_file.name)
    return tmp_file.name

# --- Streamlit UI ---

st.set_page_config(page_title="🪐 Astrology Dasha Report", layout="centered")
st.title("🪐 Personalized Dasha Astrology Report Generator")

with st.form("birth_form"):
    name = st.text_input("Your Full Name")
    dob = st.date_input("Date of Birth")
    tob = st.time_input("Time of Birth")
    latitude = st.number_input("Latitude (+North / -South)", format="%.6f")
    longitude = st.number_input("Longitude (+East / -West)", format="%.6f")
    submitted = st.form_submit_button("Generate My Dasha Report")

if submitted:
    try:
        birth_datetime = datetime.combine(dob, tob)
        jd = swe.julday(birth_datetime.year, birth_datetime.month, birth_datetime.day,
                        birth_datetime.hour + birth_datetime.minute / 60)
        moon_data = swe.calc_ut(jd, swe.MOON)
        moon_lon = moon_data[0] if moon_data else 0.0

        moon_lord = get_moon_lord(moon_lon)
        dasha_periods = calculate_dasha_start(birth_datetime.year, moon_lon)

        this_year = datetime.now().year
        current_dasha = next((d for d in dasha_periods if d[1] <= this_year <= d[2]), None)
        career, love, health = DASHA_PREDICTIONS.get(current_dasha[0], ("Balanced career", "Steady love life", "Normal health"))

        st.subheader(f"🌕 Your Moon Nakshatra Lord: `{moon_lord}`")
        st.markdown(f"**📅 Current Mahadasha:** `{current_dasha[0]}` ({current_dasha[1]} - {current_dasha[2]})")
        st.write(f"💼 **Career:** {career}")
        st.write(f"❤️ **Love:** {love}")
        st.write(f"🧘 **Health:** {health}")

        # Generate PDF and offer download
        pdf_path = generate_pdf(name, birth_datetime, latitude, longitude, moon_lord, current_dasha, career, love, health, dasha_periods)
        with open(pdf_path, "rb") as f:
            st.download_button(label="📥 Download PDF Report",
                               data=f,
                               file_name=f"{name.replace(' ', '_')}_dasha_report.pdf",
                               mime="application/pdf")
        os.remove(pdf_path)

    except Exception as e:
        st.error(f"Something went wrong: {e}")

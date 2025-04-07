from skyfield.api import load
from datetime import datetime, timedelta
from fpdf import FPDF

# Vimshottari Dasha Data
DASHA_YEARS = {
    'Ketu': 7, 'Venus': 20, 'Sun': 6, 'Moon': 10, 'Mars': 7,
    'Rahu': 18, 'Jupiter': 16, 'Saturn': 19, 'Mercury': 17
}
DASHA_SEQUENCE = ['Ketu', 'Venus', 'Sun', 'Moon', 'Mars', 'Rahu', 'Jupiter', 'Saturn', 'Mercury']
TOTAL_DASHA_YEARS = sum(DASHA_YEARS.values())

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

def calculate_antardashas(mahadasa_lord, start_year):
    duration = DASHA_YEARS[mahadasa_lord]
    antardasha_list = []
    start_date = datetime(start_year, 1, 1)
    total_days = int(duration * 365.25)

    current_start = start_date
    for sub_lord in DASHA_SEQUENCE:
        proportion = DASHA_YEARS[sub_lord] / 120
        sub_duration_days = int(proportion * duration * 365.25)
        end_date = current_start + timedelta(days=sub_duration_days)
        antardasha_list.append((sub_lord, current_start.date(), end_date.date()))
        current_start = end_date

    return antardasha_list

# -- INPUT SECTION --
name = input("Enter your name: ")
dob_str = input("Enter your date of birth (YYYY-MM-DD): ")
tob_str = input("Time of birth (HH:MM, 24hr): ")

while True:
    try:
        longitude = float(input("Enter longitude (East=+, West=-): "))
        break
    except ValueError:
        print("Invalid input. Please enter a numeric value for longitude.")

while True:
    try:
        latitude = float(input("Enter latitude (North=+, South=-): "))
        break
    except ValueError:
        print("Invalid input. Please enter a numeric value for latitude.")

# -- MOON POSITION CALCULATION --
try:
    dob = datetime.strptime(f"{dob_str} {tob_str}", "%Y-%m-%d %H:%M")
    eph = load('de421.bsp')
    ts = load.timescale()
    t = ts.utc(dob.year, dob.month, dob.day, dob.hour, dob.minute)
    earth, moon = eph['earth'], eph['moon']
    astrometric = earth.at(t).observe(moon).apparent()
    _, moon_lon, _ = astrometric.ecliptic_latlon()
    moon_lon = moon_lon.degrees
except Exception as e:
    print(f"Error calculating Moon longitude: {e}")
    moon_lon = 0.0

# -- DASHA CALCULATION --
moon_lord = get_moon_lord(moon_lon)
dasha_periods = calculate_dasha_start(dob.year, moon_lon)

this_year = datetime.now().year
current_dasha = next((d for d in dasha_periods if d[1] <= this_year <= d[2]), None)
if current_dasha:
    career, love, health = DASHA_PREDICTIONS.get(current_dasha[0], ("Balanced career", "Steady love life", "Normal health"))
else:
    current_dasha = ("Unknown", this_year, this_year)
    career, love, health = ("Balanced career", "Steady love life", "Normal health")

# -- PDF REPORT GENERATION --
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
pdf.cell(200, 10, txt="Predictions for the Current Year:", ln=True)
pdf.cell(200, 10, txt=f"Career: {career}", ln=True)
pdf.cell(200, 10, txt=f"Love: {love}", ln=True)
pdf.cell(200, 10, txt=f"Health: {health}", ln=True)
pdf.ln(10)

# Mahadasha Periods
pdf.set_font("Arial", 'B', 12)
pdf.cell(200, 10, txt="Upcoming Mahadasha Periods:", ln=True)
pdf.set_font("Arial", size=11)
for lord, start, end in dasha_periods:
    pdf.cell(200, 10, txt=f"{lord}: {start} - {end}", ln=True)

# Antardasha for Current Mahadasha
pdf.ln(10)
pdf.set_font("Arial", 'B', 12)
pdf.cell(200, 10, txt=f"Antardashas within {current_dasha[0]} Mahadasha:", ln=True)
pdf.set_font("Arial", size=11)
antars = calculate_antardashas(current_dasha[0], current_dasha[1])
for lord, start, end in antars:
    pdf.cell(200, 10, txt=f"{lord}: {start} to {end}", ln=True)

# Save PDF
pdf.output("dasha_report_with_antardasha.pdf")
print("✅ PDF report with Antardasha saved as 'dasha_report_with_antardasha.pdf'")

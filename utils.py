# utils.py
import re
import json
from fpdf import FPDF
import io

def build_prompt(origin, destination, days, budget, travel_style, student_card):
    prompt = f"""
You are a helpful travel planner for budget-conscious students. Provide a detailed {days}-day itinerary from {origin} to {destination}. Keep total estimated cost under INR {budget}.
List per-day schedule with places to visit, approximate time, transport suggestion (cheap), one recommended budget meal, and one hostel/cheap stay option. If student_card is True, include any likely student discounts or passes that exist for the city.
Also provide a short list of coordinates for main points in JSON format labeled 'POINTS' at the end.
Be concise but actionable.
"""
    return prompt

def extract_text_from_gemini_response(resp):
    # The python-genai response structure can vary; this adapter grabs main text.
    # Example: resp.candidates[0].content[0].text  (check actual SDK)
    try:
        return resp.text or resp["candidates"][0]["content"][0]["text"]
    except Exception:
        return str(resp)

def parse_itinerary_text(text):
    # Very simple parsing: split by "Day X" blocks
    day_blocks = re.split(r"(?:Day\s+\d+:?)", text)
    day_plans = [b.strip() for b in day_blocks if b.strip()]
    # Extract fake places with coords from a JSON block named POINTS
    places = []
    m = re.search(r"POINTS[:\s]*(\{.*\})", text, re.S)
    if m:
        try:
            data = json.loads(m.group(1))
            for p in data.get("points", []):
                places.append({"name": p.get("name"), "latlon": (p["lat"], p["lon"]), "notes": p.get("note","")})
        except Exception:
            pass
    return day_plans, places

def estimate_cost(places, days, travel_style):
    base = 500 * days
    if travel_style == "Comfort budget": base *= 1.6
    if travel_style == "Backpacking": base *= 0.7
    # add simple per-place cost
    place_cost = 100 * len(places)
    return int(base + place_cost)

def render_summary_card(destination, days, budget, cost_estimate):
    return f"""
    <div class="card">
      <h2>{destination} — {days} days</h2>
      <p>Estimated cost: <strong>INR {cost_estimate}</strong> (Your budget: INR {budget})</p>
    </div>
    """

def itinerary_to_pdf(destination, origin, day_plans, cost_estimate):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=14)
    pdf.cell(200, 10, txt=f"{origin} → {destination} Itinerary", ln=True, align='C')
    pdf.ln(4)
    for i, day in enumerate(day_plans, 1):
        pdf.set_font("Arial", size=12)
        pdf.multi_cell(0, 8, txt=f"Day {i}:\n{day}")
        pdf.ln(2)
    pdf.ln(4)
    pdf.set_font("Arial", size=12)
    pdf.cell(0, 8, txt=f"Estimated cost: INR {cost_estimate}", ln=True)
    out = io.BytesIO()
    pdf.output(out)
    return out.getvalue()

def save_plan_to_csv(destination, origin, day_plans, cost_estimate):
    import csv
    rows = []
    for i, d in enumerate(day_plans, 1):
        rows.append([destination, origin, f"Day {i}", d, cost_estimate])
    with open("plans.csv", "a", newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerows(rows)

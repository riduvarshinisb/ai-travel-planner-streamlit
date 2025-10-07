# app.py
import os
import streamlit as st
from google_genai import Client   # google genai python client (python-genai)
import folium
from streamlit_folium import st_folium
from fpdf import FPDF
import pandas as pd
import utils
from dotenv import load_dotenv

# Load local .env (for local development)
load_dotenv()

# Page config and basic styling
st.set_page_config(page_title="AI Travel Planner — Students", layout="centered")
with open("assets/dark-theme.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

st.markdown('<div class="app-header"> \
  <h1>AI Travel Planner — Students</h1> \
  <p class="subtitle">Personalized, budget-friendly plans powered by Gemini</p> \
</div>', unsafe_allow_html=True)

# Initialize Gemini client
GEMINI_KEY = os.getenv("GEMINI_API_KEY") or st.secrets.get("GEMINI_API_KEY")
if not GEMINI_KEY:
    st.warning("GEMINI_API_KEY not found. Set it in your environment or Secrets.")
client = Client(api_key=GEMINI_KEY)

# Sidebar: user inputs
with st.sidebar:
    st.header("Trip inputs")
    origin = st.text_input("Origin (city or landmark)", value="Bengaluru")
    destination = st.text_input("Destination (city or landmark)", value="Goa")
    days = st.number_input("Trip length (days)", min_value=1, max_value=14, value=3)
    budget = st.number_input("Total budget (INR)", min_value=500, value=6000, step=100)
    travel_style = st.selectbox("Travel style", ["Backpacking", "Comfort budget", "Sightseeing", "Nightlife"])
    student_card = st.checkbox("I have a student ID (show student deals)", value=True)
    generate_button = st.button("Generate Itinerary")

st.sidebar.markdown("---")
st.sidebar.write("Tips:")
st.sidebar.write("- Try lower budget to get hostels & cheap eats.")
st.sidebar.write("- Use 'Share' to export the itinerary.")

# Helper to call Gemini
def call_gemini_prompt(prompt: str, temperature: float = 0.2, max_output_tokens: int = 800):
    # Using google-genai's Client generateContent style usage
    # (This is illustrative; check client docs for the exact call surface.)
    response = client.generate(
        model="gemini-1.5-pro",  # choose the model you want available in your project
        input=prompt,
        temperature=temperature,
        max_output_tokens=max_output_tokens
    )
    # handle response structure
    text = utils.extract_text_from_gemini_response(response)
    return text

# Main flow
if generate_button:
    with st.spinner("Creating your personalized itinerary..."):
        # Build prompt with constraints
        prompt = utils.build_prompt(
            origin=origin,
            destination=destination,
            days=days,
            budget=budget,
            travel_style=travel_style,
            student_card=student_card
        )
        itinerary_text = call_gemini_prompt(prompt)

        # Post-process: parse suggested places (if present)
        day_plans, places = utils.parse_itinerary_text(itinerary_text)

        # Cost estimation
        cost_estimate = utils.estimate_cost(places, days, travel_style)

        # Show summary card
        st.markdown(utils.render_summary_card(destination, days, budget, cost_estimate), unsafe_allow_html=True)

        st.subheader("Itinerary")
        for i, day in enumerate(day_plans, 1):
            st.markdown(f"**Day {i}**")
            st.write(day)

        if places:
            st.subheader("Map preview")
            m = folium.Map(location=places[0]["latlon"], zoom_start=12)
            for p in places:
                folium.Marker(
                    location=p["latlon"],
                    popup=f"{p['name']} — {p.get('notes','')}"
                ).add_to(m)
            st_folium(m, width=700, height=450)

        # Offer PDF download
        if st.button("Download itinerary (PDF)"):
            pdf_bytes = utils.itinerary_to_pdf(destination, origin, day_plans, cost_estimate)
            st.download_button("Download PDF", data=pdf_bytes, file_name=f"{destination}_itinerary.pdf", mime="application/pdf")

        # Cache/save option
        if st.button("Save this plan to local CSV"):
            utils.save_plan_to_csv(destination, origin, day_plans, cost_estimate)
            st.success("Saved to plans.csv in repo (server-side).")

# Fallback UI
st.markdown("<div class='footer'>Made with ❤️ for students • Uses Gemini API</div>", unsafe_allow_html=True)

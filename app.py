import os
import streamlit as st
import google.generativeai as genai

# Configure Gemini API
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

st.set_page_config(page_title="AI Travel Planner for Students", page_icon="🌍", layout="centered")

# Custom CSS for Dark Mode UI
st.markdown("""
    <style>
    body {
        background-color: #0e1117;
        color: #FAFAFA;
        font-family: 'Poppins', sans-serif;
    }
    .stTextInput, .stNumberInput, .stTextArea {
        background-color: #262730 !important;
        color: white !important;
    }
    .stButton>button {
        background: linear-gradient(90deg, #00C6FF, #0072FF);
        color: white;
        border: none;
        padding: 0.6em 1.2em;
        border-radius: 10px;
        transition: 0.3s;
    }
    .stButton>button:hover {
        background: linear-gradient(90deg, #0072FF, #00C6FF);
        transform: scale(1.05);
    }
    </style>
""", unsafe_allow_html=True)

st.title("AI Travel Planner for Students")
st.write("Plan your next trip smartly, affordably, and effortlessly!")

destination = st.text_input("🌍 Destination")
budget = st.number_input("💰 Budget (in INR)", min_value=1000, step=500)
days = st.number_input("🗓️ Number of Days", min_value=1, step=1)
interests = st.text_area("🎯 Interests (e.g., adventure, history, food, beaches)")

if st.button("Generate Itinerary"):
    with st.spinner("Planning your trip..."):
        prompt = f"""
        You are a smart travel planner for students.
        Create a personalized, budget-friendly {days}-day trip to {destination}.
        Consider a total budget of ₹{budget}.
        Focus on student-friendly accommodations, food, and transport.
        Interests: {interests}.
        Provide a day-by-day itinerary with tips and cost breakdown.
        """

        model = genai.GenerativeModel("gemini-pro")
        response = model.generate_content(prompt)

        st.subheader("Your AI-Generated Itinerary")
        st.markdown(response.text)

st.markdown("---")
st.caption("Built using Streamlit + Gemini AI")

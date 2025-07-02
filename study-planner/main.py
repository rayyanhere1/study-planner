import streamlit as st
import random
import os
from dotenv import load_dotenv
from datetime import datetime
import pandas as pd
import google.generativeai as genai
import re

st.set_page_config(page_title="StudyMate.ai", page_icon="🎓", layout="wide")

st.markdown('''
    <style>
    div[data-testid="stFormSubmitButton"] button {
        background: linear-gradient(90deg, #6366f1 0%, #818cf8 100%);
        color: #fff;
        border: none;
        border-radius: 8px;
        font-weight: 700;
        font-size: 1.15rem;
        padding: 0.7rem 2.2rem;
        margin-top: 0.7rem;
        margin-bottom: 0.5rem;
        box-shadow: 0 2px 8px 0 rgba(80, 112, 255, 0.10);
        cursor: pointer;
        transition: 0.2s;
        width: 100%;
        max-width: 400px;
    }
    div[data-testid="stFormSubmitButton"] button:hover {
        background: linear-gradient(90deg, #818cf8 0%, #6366f1 100%);
        color: #fff;
        transform: translateY(-2px) scale(1.04);
    }
    .stTextInput>div>div>input,
    .stSelectbox>div>div>div>input,
    .stSlider>div {
        width: 100% !important;
        min-width: 0 !important;
        box-sizing: border-box;
    }
    @media (max-width: 600px) {
        .stTextInput>div>div>input,
        .stSelectbox>div>div>div>input,
        .stSlider>div {
            font-size: 1.05rem !important;
            padding: 0.5rem !important;
        }
        div[data-testid="stFormSubmitButton"] button {
            font-size: 1rem;
            padding: 0.6rem 1.2rem;
        }
        .stDataFrame thead tr th {
            font-size: 0.95rem !important;
        }
        .stDataFrame tbody tr td {
            font-size: 0.95rem !important;
        }
    }
    </style>
''', unsafe_allow_html=True)

load_dotenv()
gemini_api_key = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=gemini_api_key)

# --- Motivational Quotes ---
quotes = [
    "📚 *Parhna ibadat hai* — make every moment count!",
    "🌟 'Seek knowledge from cradle to grave.'",
    "🚀 Hard work beats talent when talent doesn't work hard.",
    "🕊️ Study like it's your last exam — har waqt mehnat karo!",
    "💡 Focus now, chill forever 😎"
]

# --- Study Plan Generator ---
def generate_study_plan(subjects, hours, days):
    plan = []
    per_subject_time = (int(hours) * int(days)) // len(subjects.split(","))
    for sub in subjects.split(","):
        plan.append({"Subject": sub.strip(), "Total Hours": per_subject_time})
    return plan

# --- Ask Gemini Agent ---
def ask_gemini(prompt):
    try:
        model = genai.GenerativeModel("gemini-2.0-flash")
        response = model.generate_content(prompt)
        result_str = getattr(response, "_result", "")
        match = re.search(r'text: "(.*?)"', result_str, re.DOTALL)
        if match:
            text = match.group(1).replace('\\n', '\n')
            return text
        return "No AI response received."
    except Exception as e:
        st.error(f"Gemini Error: {e}")
        return "Error: Could not get AI response."

# --- Resource Suggestions ---
subject_resources = {
    "Math": [
        "Khan Academy: https://www.khanacademy.org/math",
        "PatrickJMT: https://www.youtube.com/user/patrickJMT",
        "Paul's Online Math Notes: https://tutorial.math.lamar.edu/"
    ],
    "Physics": [
        "MinutePhysics: https://www.youtube.com/user/minutephysics",
        "Physics Classroom: https://www.physicsclassroom.com/",
        "MIT OpenCourseWare: https://ocw.mit.edu/courses/physics/"
    ],
    "Chemistry": [
        "CrashCourse Chemistry: https://www.youtube.com/playlist?list=PL8dPuuaLjXtPHzzYuWy6fYEaX9mQQ8oGr",
        "Khan Academy Chemistry: https://www.khanacademy.org/science/chemistry",
        "Chemguide: https://www.chemguide.co.uk/"
    ]
}

generic_resources = [
    "YouTube: https://www.youtube.com/",
    "Wikipedia: https://www.wikipedia.org/",
    "Khan Academy: https://www.khanacademy.org/",
    "Coursera: https://www.coursera.org/",
    "Google Scholar: https://scholar.google.com/"
]

# --- Streamlit UI ---
st.title("🎓 StudyMate.ai")
st.subheader("Apka personal AI Study Planner 📅")

st.markdown("---")

with st.form("study_form"):
    subjects = st.text_input("📘 Subjects (comma separated)", "Math, Physics, Chemistry")
    hours = st.selectbox("⏰ Daily Study Hours", [2, 3, 4, 5, 6])
    days = st.slider("📆 Days Left Till Exam", 1, 60, 30)
    motivation = st.checkbox("💡 Show Motivational Quote")
    ai_tips = st.checkbox("🧠 Get Smart Study Tips from AI")
    show_resources = st.checkbox("🔗 Show Resource Suggestions")
    submitted = st.form_submit_button("✨ Generate Plan")

if submitted:
    st.markdown("### 📅 Your Study Plan")
    plan_data = generate_study_plan(subjects, hours, days)
    df = pd.DataFrame(plan_data)
    st.dataframe(df, use_container_width=True)
    # Download as TXT (keep as before)
    plan_text = "\n".join([f"{row['Subject']} → {row['Total Hours']} hours total" for row in plan_data])
    st.download_button("⬇️ Download Plan as TXT", plan_text, file_name="study_plan.txt")

    # --- AI Tips/Plan First ---
    if ai_tips:
        st.markdown("### 🤖 AI Tips")
        ai_response = ask_gemini(f"Give smart study tips for {subjects} in {days} days, {hours} hours per day.")
        st.success(ai_response)

    # --- Resource Suggestions Second ---
    if show_resources:
        st.markdown("### 📚 Resource Suggestions")
        for sub in subjects.split(","):
            sub = sub.strip()
            if sub in subject_resources:
                st.markdown(f"**{sub}:**")
                for res in subject_resources[sub]:
                    st.markdown(f"- {res}")
            else:
                st.markdown(f"**{sub}:** (General Resources)")
                for res in generic_resources:
                    st.markdown(f"- {res}")

    # --- Motivation Last ---
    if motivation:
        st.markdown("### 🌟 Motivation of the Day")
        st.info(random.choice(quotes))

st.markdown("---")
st.caption("💻 Made with 🤍 by Rayyan")

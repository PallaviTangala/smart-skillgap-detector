import streamlit as st
import pdfplumber
import json
import plotly.express as px
import os

# ---------------- USER AUTH SYSTEM ----------------
USER_FILE = "users.json"

def load_users():
    if os.path.exists(USER_FILE):
        with open(USER_FILE, "r") as f:
            return json.load(f)
    return {}

def save_users(users):
    with open(USER_FILE, "w") as f:
        json.dump(users, f)

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.username = ""

if "history" not in st.session_state:
    st.session_state.history = []

users = load_users()

# ---------------- PAGE CONFIG ----------------
st.set_page_config(
    page_title="AI Career Copilot",
    page_icon="🚀",
    layout="wide"
)

# ---------------- LOGIN / SIGNUP ----------------
if not st.session_state.logged_in:

    st.title("🔐 Login / Signup")

    choice = st.radio("Select Option", ["Login", "Signup"])

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if choice == "Signup":
        if st.button("Create Account"):
            if username in users:
                st.error("User already exists!")
            else:
                users[username] = password
                save_users(users)
                st.success("Account created! Please login.")

    if choice == "Login":
        if st.button("Login"):
            if username in users and users[username] == password:
                st.session_state.logged_in = True
                st.session_state.username = username
                st.rerun()
            else:
                st.error("Invalid credentials")

    st.stop()

# ---------------- LOGOUT ----------------
st.sidebar.write(f"👤 Logged in as: {st.session_state.username}")

if st.sidebar.button("Logout"):
    st.session_state.logged_in = False
    st.session_state.username = ""
    st.rerun()

# ---------------- DARK MODE ----------------
dark_mode = st.toggle("🌙 Dark Mode")

if dark_mode:
    bg_color = "linear-gradient(135deg,#0f172a,#1e293b)"
    card_color = "rgba(30,41,59,0.7)"
    text_color = "#ffffff"
else:
    bg_color = "linear-gradient(135deg,#d6e6f5,#b8d2ea)"
    card_color = "rgba(255,255,255,0.85)"
    text_color = "#0f172a"

# ---------------- UI STYLE ----------------
st.markdown(f"""
<style>
.stApp {{
    background: {bg_color};
}}

.card {{
    background: {card_color};
    backdrop-filter: blur(12px);
    padding:25px;
    border-radius:20px;
    box-shadow:0px 8px 30px rgba(0,0,0,0.2);
    margin-bottom:20px;
    color:{text_color} !important;
    animation: fadeInUp 0.8s ease;
}}

.card:hover {{
    transform: scale(1.03);
}}

h1,h2,h3,h4,h5,p,li,span,div {{
    color:{text_color} !important;
}}

.skill {{
    background:#2563eb;
    color:white !important;
    padding:8px 14px;
    border-radius:20px;
    margin:5px;
}}

.required {{
    background:#3b82f6;
    color:white !important;
    padding:8px 14px;
    border-radius:20px;
    margin:5px;
}}

.missing {{
    background:#ef4444;
    color:white !important;
    padding:8px 14px;
    border-radius:20px;
    margin:5px;
}}

@keyframes fadeInUp {{
    from {{opacity:0; transform:translateY(30px);}}
    to {{opacity:1; transform:translateY(0);}}
}}
</style>
""", unsafe_allow_html=True)

# ---------------- LOAD SKILLS ----------------
with open("skills_db.json") as f:
    skills_db = json.load(f)

# ---------------- FUNCTIONS ----------------
def extract_resume_text(file):
    text = ""
    with pdfplumber.open(file) as pdf:
        for page in pdf.pages:
            if page.extract_text():
                text += page.extract_text()
    return text


def extract_skills(resume_text):
    found_skills = []
    resume_text = resume_text.lower()

    for job in skills_db:
        for skill in skills_db[job]:
            if skill.lower() in resume_text:
                found_skills.append(skill)

    return list(set(found_skills))


def career_suggestions(user_skills):
    suggestions = []
    for job in skills_db:
        required = skills_db[job]
        match = len(set(user_skills) & set(required))
        if match >= 2:
            suggestions.append(job)
    return suggestions[:5]


def learning_roadmap(missing):
    return [f"Month {i+1}: Learn {skill}" for i, skill in enumerate(missing)]


def learning_resources(missing):
    resources = {}
    for skill in missing:
        resources[skill] = {
            "Course": f"https://www.coursera.org/search?query={skill.replace(' ', '%20')}",
            "YouTube": f"https://www.youtube.com/results?search_query={skill.replace(' ', '+')}+tutorial",
            "Project": f"Build a real-world project using {skill}"
        }
    return resources


def resume_feedback(text):
    feedback = []
    if len(text) < 500:
        feedback.append("⚠️ Resume is too short.")
    if "python" not in text.lower():
        feedback.append("💡 Add Python skill.")
    if "project" not in text.lower():
        feedback.append("📌 Add projects.")
    if "machine learning" not in text.lower():
        feedback.append("🤖 Add AI/ML skills.")
    if not feedback:
        feedback.append("✅ Resume looks strong!")
    return feedback

# ---------------- TITLE ----------------
st.markdown(f"""
<h1 style='text-align:center;'>🚀 AI Career Copilot</h1>
<p style='text-align:center;'>Welcome, {st.session_state.username} 👋</p>
""", unsafe_allow_html=True)

st.divider()

# ---------------- DASHBOARD ----------------
st.markdown("## 📊 User Dashboard")

if st.session_state.history:
    latest = st.session_state.history[-1]

    col1, col2, col3 = st.columns(3)
    col1.metric("🎯 Role", latest["job"])
    col2.metric("📊 Score", f"{latest['score']}%")
    col3.metric("🧠 Skills", len(latest["skills"]))

    scores = [h["score"] for h in st.session_state.history]
    st.line_chart(scores)
else:
    st.info("Upload resume to see dashboard.")

st.divider()

# ---------------- INPUT ----------------
col1, col2 = st.columns(2)

with col1:
    dream_job = st.text_input("🎯 Enter Dream Job")

with col2:
    resume = st.file_uploader("📄 Upload Resume", type=["pdf"])

# ---------------- PROCESS ----------------
if resume:

    text = extract_resume_text(resume)

    st.markdown('<div class="card"><h3>📄 Resume Content</h3></div>', unsafe_allow_html=True)
    st.write(text)

    st.markdown('<div class="card"><h3>🧠 AI Feedback</h3></div>', unsafe_allow_html=True)
    for tip in resume_feedback(text):
        st.write(tip)

    user_skills = extract_skills(text)

    st.markdown('<div class="card"><h3>🧠 Skills</h3></div>', unsafe_allow_html=True)
    for s in user_skills:
        st.markdown(f'<span class="skill">{s}</span>', unsafe_allow_html=True)

    st.markdown('<div class="card"><h3>💼 Careers</h3></div>', unsafe_allow_html=True)
    for c in career_suggestions(user_skills):
        st.write("👉", c)

    if dream_job in skills_db:

        required = skills_db[dream_job]
        missing = list(set(required) - set(user_skills))

        match = len(set(user_skills) & set(required))
        score = int((match / len(required)) * 100)

        st.session_state.history.append({
            "job": dream_job,
            "score": score,
            "skills": user_skills
        })

        st.progress(score/100)
        st.write(f"Score: {score}%")

        st.markdown('<div class="card"><h3>📚 Resources</h3></div>', unsafe_allow_html=True)

        for skill, res in learning_resources(missing).items():
            st.markdown(f"### {skill}")
            st.markdown(f"[📘 Course]({res['Course']})")
            st.markdown(f"[📺 YouTube]({res['YouTube']})")
            st.markdown(f"🛠 {res['Project']}")
            st.divider()
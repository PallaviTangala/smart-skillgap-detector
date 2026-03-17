import streamlit as st
import pdfplumber
import json
import os
import urllib.parse
import random

# ---------------- USER AUTH ----------------
USER_FILE = "users.json"

def load_users():
    if os.path.exists(USER_FILE):
        try:
            with open(USER_FILE, "r") as f:
                return json.load(f)
        except:
            return {}
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
st.set_page_config(page_title="AI Career Copilot", page_icon="🚀", layout="wide")

# ---------------- LOGIN ----------------
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

# ---------------- UI ----------------
st.markdown("""
<style>

/* Background */
.stApp {
    background: linear-gradient(135deg,#0f172a,#1e293b);
}

/* Title */
h1 {
    text-align:center;
    color:white !important;
}

/* Subtitle */
.subtitle {
    text-align:center;
    color:#cbd5f5;
}

/* Card */
.card {
    background: rgba(255,255,255,0.95);
    padding:25px;
    border-radius:20px;
    margin-bottom:20px;
    box-shadow:0px 10px 30px rgba(0,0,0,0.2);
    animation: fadeUp 0.6s ease;
    color:#0f172a !important;
}

/* Skills */
.skill {
    background:#2563eb;
    color:white !important;
    padding:6px 12px;
    border-radius:15px;
    margin:5px;
    display:inline-block;
}

/* Resume box */
.resume-box {
    max-height:300px;
    overflow-y:auto;
    background:white;
    padding:10px;
    border-radius:10px;
    color:#0f172a;
}

/* Animation */
@keyframes fadeUp {
    from {opacity:0; transform:translateY(20px);}
    to {opacity:1; transform:translateY(0);}
}

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

def extract_skills(text):
    found = []
    text = text.lower()
    for job in skills_db:
        for skill in skills_db[job]:
            if skill.lower() in text:
                found.append(skill)
    return list(set(found))

def resume_feedback(text):
    feedback = []
    if len(text) < 500:
        feedback.append("⚠️ Add more details to your resume")
    if "project" not in text.lower():
        feedback.append("📌 Add project experience")
    if "python" not in text.lower():
        feedback.append("💡 Add Python skill")
    if not feedback:
        feedback.append("✅ Strong resume")
    return feedback

def learning_resources(missing):

    # 🎯 SMART PROJECT IDEAS
    project_map = {
        "Pandas": "Analyze Netflix or IPL dataset and generate insights",
        "NumPy": "Build a matrix calculator with advanced operations",
        "Statistics": "Create a student performance analysis dashboard",
        "Tableau": "Build an interactive sales dashboard",
        "Power BI": "Create a business insights dashboard",
        "Python": "Build a task manager or automation tool",
        "SQL": "Design and query a student database system",
        "Machine Learning": "Build a house price prediction model",
        "Deep Learning": "Create an image classification model",
        "HTML": "Build a personal portfolio website",
        "CSS": "Design a responsive landing page",
        "JavaScript": "Create a dynamic to-do list web app",
        "React": "Build a job listing web application",
        "Django": "Develop a blog or CRUD web app",
        "Flask": "Create a REST API for a mini project",
        "Excel": "Create a financial dashboard using pivot tables"
    }

    res = {}

    for skill in missing:
        query = urllib.parse.quote(skill)

        # 🎯 Use specific project if available
        project = project_map.get(
            skill,
            f"Build a real-world application using {skill}"
        )

        res[skill] = {
            "course": f"https://www.coursera.org/search?query={query}",
            "youtube": f"https://www.youtube.com/results?search_query={query}+full+course",
            "project": project
        }

    return res

# ---------------- TITLE ----------------
st.markdown("<h1>🚀 AI Career Copilot</h1><p class='subtitle'>Analyze your resume • Find skill gaps • Learn smarter</p>", unsafe_allow_html=True)

# ---------------- INPUT ----------------
col1, col2 = st.columns(2)

with col1:
    dream_job = st.text_input("🎯 Dream Job")

with col2:
    resume = st.file_uploader("📄 Upload Resume", type=["pdf"])

# ---------------- PROCESS ----------------
if resume:

    with st.spinner("🔍 AI analyzing your resume..."):
        text = extract_resume_text(resume)

    st.markdown("<div class='card'><h3>📄 Resume Content</h3></div>", unsafe_allow_html=True)

    st.markdown(f"""
    <div class='resume-box'>
    {text}
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<div class='card'><h3>🧠 AI Feedback</h3></div>", unsafe_allow_html=True)
    for f in resume_feedback(text):
        st.write(f)

    skills = extract_skills(text)

    st.markdown("<div class='card'><h3>🧠 Your Skills</h3></div>", unsafe_allow_html=True)
    for s in skills:
        st.markdown(f"<span class='skill'>{s}</span>", unsafe_allow_html=True)

    if dream_job in skills_db:
        required = skills_db[dream_job]
        missing = list(set(required) - set(skills))

        score = int((len(set(skills)&set(required))/len(required))*100)

        st.markdown("<div class='card'><h3>📊 Skill Match Score</h3></div>", unsafe_allow_html=True)
        st.progress(score/100)
        st.write(f"### {score}% Match")

        st.session_state.history.append({
            "job": dream_job,
            "score": score,
            "skills": skills
        })

        st.markdown("<div class='card'><h3>📚 Learning Resources</h3></div>", unsafe_allow_html=True)

        for skill, val in learning_resources(missing).items():

            st.markdown(f"<div class='card'><h3>📌 {skill}</h3></div>", unsafe_allow_html=True)

            st.markdown(f"🎓 **Coursera course for {skill}:**")
            st.markdown(f"[Start learning {skill}]({val['course']})")

            st.markdown(f"📺 **YouTube tutorial for {skill}:**")
            st.markdown(f"[Watch full tutorial]({val['youtube']})")

            st.markdown(f"🛠 **Project:** {val['project']}")

            st.divider()
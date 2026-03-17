<<<<<<< HEAD
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
=======
import streamlit as st
import pdfplumber
import json
import plotly.express as px

# ---------------- PAGE CONFIG ----------------
st.set_page_config(
    page_title="AI Career Copilot",
    page_icon="🚀",
    layout="wide"
)

# ---------------- UI STYLE ----------------
st.markdown("""
<style>

@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;500;700;900&display=swap');

html, body, [class*="css"] {
    font-family: 'Poppins', sans-serif;
}

/* Background */

.stApp{
    background: linear-gradient(135deg,#d6e6f5,#b8d2ea);
}

/* Big Animated Title */

.title{
    text-align:center;
    font-size:90px;
    font-weight:900;
    letter-spacing:3px;

    background: linear-gradient(90deg,#0d47a1,#1976d2,#42a5f5);
    -webkit-background-clip:text;
    -webkit-text-fill-color:transparent;

    animation: slideDown 1s ease-out;
}

/* Subtitle */

.subtitle{
    text-align:center;
    font-size:24px;
    color:#0f172a;
}

/* Headings fix */

h1,h2,h3,h4,h5{
    color:#1e3a8a !important;
}

/* Normal text */

p,li,span,div{
    color:#0f172a !important;
    font-size:17px;
}

/* Input box */

input{
    background:#1e293b !important;
    color:white !important;
    border-radius:8px !important;
}

/* File uploader */

.stFileUploader{
    background:#1e293b !important;
    padding:10px;
    border-radius:10px;
    color:white !important;
}

/* Cards */

.card{
    background:#ffffff;
    padding:25px;
    border-radius:15px;
    box-shadow:0px 6px 25px rgba(0,0,0,0.15);
    margin-bottom:20px;
}

/* Skill tags */

.skill{
    display:inline-block;
    background:#2563eb;
    color:white !important;
    padding:8px 14px;
    border-radius:20px;
    margin:5px;
}

/* Required skills */

.required{
    display:inline-block;
    background:#3b82f6;
    color:white !important;
    padding:8px 14px;
    border-radius:20px;
    margin:5px;
}

/* Missing skills */

.missing{
    display:inline-block;
    background:#ef4444;
    color:white !important;
    padding:8px 14px;
    border-radius:20px;
    margin:5px;
}

/* Career suggestion cards */

.career-card{
    background:#e8f1ff;
    border-left:6px solid #2563eb;
    padding:14px;
    border-radius:8px;
    margin-bottom:10px;
    color:#1e3a8a !important;
    font-size:18px;
    font-weight:600;
}

/* Animation */

@keyframes slideDown{
    from{
        opacity:0;
        transform:translateY(-50px);
    }
    to{
        opacity:1;
        transform:translateY(0);
    }
}

</style>
""", unsafe_allow_html=True)

# ---------------- LOAD SKILL DATABASE ----------------
with open("skills_db.json") as f:
    skills_db = json.load(f)

# ---------------- FUNCTIONS ----------------
def extract_resume_text(file):

    text = ""

    with pdfplumber.open(file) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()

            if page_text:
                text += page_text

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

    roadmap = []
    month = 1

    for skill in missing:
        roadmap.append(f"Month {month}: Learn {skill}")
        month += 1

    return roadmap


def learning_resources(missing):

    resources = {}

    for skill in missing:

        resources[skill] = {
            "Course": f"Search '{skill}' course on Coursera or Udemy",
            "YouTube": f"YouTube tutorials for {skill}",
            "Project": f"Build a project using {skill}"
        }

    return resources


# ---------------- HEADER ----------------
st.markdown('<p class="title">🚀 AI Career Copilot</p>', unsafe_allow_html=True)

st.markdown('<p class="subtitle">Upload your resume and discover your career path</p>', unsafe_allow_html=True)

st.divider()

# ---------------- INPUT ----------------
col1, col2 = st.columns(2)

with col1:
    dream_job = st.text_input("🎯 Enter your Dream Job")

with col2:
    resume = st.file_uploader("📄 Upload Resume (PDF)", type=["pdf"])


# ---------------- PROCESS ----------------
if resume is not None:

    resume_text = extract_resume_text(resume)

    st.markdown('<div class="card"><h3>📄 Resume Content</h3></div>', unsafe_allow_html=True)

    st.write(resume_text)

    user_skills = extract_skills(resume_text)

    st.markdown('<div class="card"><h3>🧠 Your Skills</h3></div>', unsafe_allow_html=True)

    for skill in user_skills:
        st.markdown(f'<span class="skill">{skill}</span>', unsafe_allow_html=True)

    st.markdown('<div class="card"><h3>💼 Career Suggestions</h3></div>', unsafe_allow_html=True)

    for career in career_suggestions(user_skills):
        st.markdown(f'<div class="career-card">{career}</div>', unsafe_allow_html=True)

    if dream_job in skills_db:

        required = skills_db[dream_job]

        st.markdown('<div class="card"><h3>📌 Required Skills</h3></div>', unsafe_allow_html=True)

        for skill in required:
            st.markdown(f'<span class="required">{skill}</span>', unsafe_allow_html=True)

        missing = list(set(required) - set(user_skills))

        st.markdown('<div class="card"><h3>⚠ Missing Skills</h3></div>', unsafe_allow_html=True)

        for skill in missing:
            st.markdown(f'<span class="missing">{skill}</span>', unsafe_allow_html=True)

        # Skill Match Score
        match = len(set(user_skills) & set(required))
        score = int((match / len(required)) * 100)

        st.subheader("📊 Skill Match Score")
        st.progress(score / 100)
        st.write(f"Match Score: **{score}%**")

        # Chart
        values = []

        for skill in required:
            if skill in user_skills:
                values.append(100)
            else:
                values.append(30)

        fig = px.bar(
            x=required,
            y=values,
            labels={"x":"Skills","y":"Proficiency"},
            title="Skill Gap Visualization"
        )

        st.plotly_chart(fig)

        # Learning Roadmap
        st.markdown('<div class="card"><h3>🗺 Learning Roadmap</h3></div>', unsafe_allow_html=True)

        roadmap = learning_roadmap(missing)

        for step in roadmap:
            st.write("•", step)

        # Learning Resources
        st.markdown('<div class="card"><h3>📚 Learning Resources</h3></div>', unsafe_allow_html=True)

        resources = learning_resources(missing)

        for skill, res in resources.items():

            st.markdown(f"### {skill}")
            st.write("📘 Course:", res["Course"])
            st.write("📺 YouTube:", res["YouTube"])
            st.write("🛠 Project:", res["Project"])

    else:
        st.warning("Job role not found in database.")
>>>>>>> a8195e765382fd496f439f0a0508bcb7d77243c4

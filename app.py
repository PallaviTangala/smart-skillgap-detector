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
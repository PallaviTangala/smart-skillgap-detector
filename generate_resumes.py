import streamlit as st
import pdfplumber
import json
from openai import OpenAI

# Add your OpenAI API Key
from openai import OpenAI
import os

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Load Skill Database
with open("skills_db.json") as f:
    skills_db = json.load(f)

# Extract text from resume
def extract_resume_text(file):
    text = ""
    with pdfplumber.open(file) as pdf:
        for page in pdf.pages:
            if page.extract_text():
                text += page.extract_text()
    return text


# Extract skills from resume using AI
def extract_skills(resume_text):

    prompt = f"""
    Extract all technical skills from this resume text.
    Return only a comma separated list.

    Resume:
    {resume_text}
    """

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}]
    )

    skills = response.choices[0].message.content
    return [s.strip() for s in skills.split(",")]


# Career Suggestions
def career_suggestions(user_skills):

    prompt = f"""
    A person has these skills:
    {user_skills}

    Suggest 3 suitable tech careers.
    """

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}]
    )

    return response.choices[0].message.content


# Learning Roadmap
def learning_roadmap(dream_job, missing_skills):

    prompt = f"""
    Someone wants to become a {dream_job}.
    They are missing these skills:
    {missing_skills}

    Create a clear 6 month roadmap.
    """

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}]
    )

    return response.choices[0].message.content


# Learning Resources
def learning_resources(missing_skills):

    prompt = f"""
    Suggest learning resources for these skills:
    {missing_skills}

    Include:
    - online courses
    - youtube channels
    - project ideas
    """

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}]
    )

    return response.choices[0].message.content


# -------------------------------
# Streamlit UI
# -------------------------------

st.title("AI Career Skill Gap Analyzer")

st.write("Upload your resume and analyze your skills for your dream career.")

dream_job = st.text_input("Enter your dream job (Example: Data Scientist)")

resume = st.file_uploader("Upload your resume (PDF)", type=["pdf"])


if resume is not None:

    resume_text = extract_resume_text(resume)

    st.subheader("Extracted Resume Content")
    st.write(resume_text)

    # Extract skills from resume
    user_skills = extract_skills(resume_text)

    st.subheader("Your Skills")
    st.write(user_skills)

    if dream_job in skills_db:

        required_skills = skills_db[dream_job]

        st.subheader("Required Skills for " + dream_job)
        st.write(required_skills)

        missing_skills = list(set(required_skills) - set(user_skills))

        st.subheader("Missing Skills")
        st.write(missing_skills)

        # Career Suggestions
        st.subheader("Career Suggestions")
        st.write(career_suggestions(user_skills))

        # Learning Roadmap
        st.subheader("Learning Roadmap")
        st.write(learning_roadmap(dream_job, missing_skills))

        # Learning Resources
        st.subheader("Learning Resources")
        st.write(learning_resources(missing_skills))

    else:
        st.warning("Job role not found in database.")
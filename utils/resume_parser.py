import os
import re

from PyPDF2 import PdfReader
from docx import Document


# ==================================================
# PDF TEXT EXTRACTION
# ==================================================

def extract_text_from_pdf(file_path):

    text = ""

    reader = PdfReader(file_path)

    for page in reader.pages:

        page_text = page.extract_text()

        if page_text:
            text += page_text + "\n"

    return text.strip()


# ==================================================
# DOCX TEXT EXTRACTION
# ==================================================

def extract_text_from_docx(file_path):

    document = Document(file_path)

    text = ""

    for paragraph in document.paragraphs:

        if paragraph.text.strip():

            text += paragraph.text + "\n"

    return text.strip()


# ==================================================
# MAIN TEXT EXTRACTION
# ==================================================

def extract_resume_text(file_path):

    if not os.path.exists(file_path):

        raise FileNotFoundError(
            "Resume file not found."
        )

    extension = os.path.splitext(
        file_path
    )[1].lower()

    if extension == ".pdf":

        return extract_text_from_pdf(
            file_path
        )

    elif extension == ".docx":

        return extract_text_from_docx(
            file_path
        )

    else:

        raise ValueError(
            "Only PDF and DOCX files are supported."
        )


# ==================================================
# SKILL DETECTION
# ==================================================

def extract_skills(text):

    skills_list = [

        "Python",
        "Java",
        "C",
        "C++",
        "HTML",
        "CSS",
        "JavaScript",
        "React",
        "Node.js",
        "Flask",
        "Django",
        "SQL",
        "MySQL",
        "PostgreSQL",
        "MongoDB",
        "Git",
        "GitHub",
        "OpenCV",
        "Machine Learning",
        "Artificial Intelligence",
        "Data Structures",
        "Algorithms",
        "Bootstrap",
        "REST API",
        "AWS",
        "Docker"
    ]

    found_skills = []

    text_lower = text.lower()

    for skill in skills_list:

        if skill.lower() in text_lower:

            found_skills.append(skill)

    return found_skills


# ==================================================
# EDUCATION DETECTION
# ==================================================

def extract_education(text):

    education_keywords = [

        "BCA",
        "B.Tech",
        "BTech",
        "MCA",
        "M.Tech",
        "MBA",
        "B.Sc",
        "M.Sc",
        "Bachelor",
        "Master",
        "Intermediate",
        "12th",
        "10th"
    ]

    found_education = []

    text_lower = text.lower()

    for education in education_keywords:

        if education.lower() in text_lower:

            found_education.append(
                education
            )

    return found_education


# ==================================================
# PROJECT DETECTION
# ==================================================

def extract_projects(text):

    lines = text.splitlines()

    projects = []

    inside_project_section = False

    for line in lines:

        clean_line = line.strip()

        if not clean_line:
            continue

        lower_line = clean_line.lower()

        if (
            "project" in lower_line
            or "projects" in lower_line
        ):

            inside_project_section = True

            continue

        if inside_project_section:

            if any(
                section in lower_line
                for section in [
                    "education",
                    "experience",
                    "skills",
                    "certification",
                    "achievement",
                    "hobbies"
                ]
            ):

                break

            if len(clean_line) > 5:

                projects.append(
                    clean_line
                )

    return projects[:10]


# ==================================================
# EXPERIENCE DETECTION
# ==================================================

def extract_experience(text):

    experience_keywords = [

        "internship",
        "intern",
        "experience",
        "developer",
        "software engineer",
        "web developer",
        "python developer",
        "java developer",
        "freelance"
    ]

    found_experience = []

    text_lower = text.lower()

    for keyword in experience_keywords:

        if keyword in text_lower:

            found_experience.append(
                keyword.title()
            )

    return list(
        dict.fromkeys(found_experience)
    )


# ==================================================
# RESUME SCORE
# ==================================================

def calculate_resume_score(
    text,
    skills,
    education,
    projects,
    experience
):

    score = 0

    # Resume has content
    if len(text) > 200:
        score += 20

    # Skills
    if len(skills) >= 5:
        score += 25

    elif len(skills) >= 3:
        score += 18

    elif len(skills) >= 1:
        score += 10

    # Education
    if education:
        score += 20

    # Projects
    if len(projects) >= 2:
        score += 20

    elif len(projects) >= 1:
        score += 10

    # Experience
    if experience:
        score += 15

    return min(score, 100)


# ==================================================
# RESUME ANALYSIS
# ==================================================

def analyze_resume(text):

    skills = extract_skills(text)

    education = extract_education(text)

    projects = extract_projects(text)

    experience = extract_experience(text)

    score = calculate_resume_score(
        text,
        skills,
        education,
        projects,
        experience
    )

    suggestions = []

    if not skills:

        suggestions.append(
            "Add a clear Technical Skills section."
        )

    elif len(skills) < 5:

        suggestions.append(
            "Add more relevant technical skills."
        )

    if not education:

        suggestions.append(
            "Add your education details."
        )

    if not projects:

        suggestions.append(
            "Add at least one or two technical projects."
        )

    if not experience:

        suggestions.append(
            "Add internships, training, or relevant experience if available."
        )

    if len(text) < 300:

        suggestions.append(
            "Your resume contains very little information. "
            "Add more relevant details."
        )

    if not suggestions:

        suggestions.append(
            "Your resume contains the main sections. "
            "Keep improving it with measurable achievements."
        )

    return {

        "score": score,

        "skills": skills,

        "education": education,

        "projects": projects,

        "experience": experience,

        "suggestions": suggestions

    }
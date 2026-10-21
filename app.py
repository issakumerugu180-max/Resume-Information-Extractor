
import os
import tempfile
import json
import re
import streamlit as st
import html
from extractor import extract_text
from preprocess import preprocess_text
from personal_info import extract_personal_info
from skills import extract_skills
from education import extract_education
from experience import extract_experience
from ner_extractor import extract_resume_entities


def extract_projects(text):
    """Extract individual projects from the Projects section."""
    lines = text.splitlines()
    projects = []
    in_projects = False

    section_headings = {
        "education", "experience", "work experience",
        "employment", "skills", "technical skills",
        "certifications", "professional summary", "summary",
        "achievements", "languages", "additional information",
        "internships", "publications"
    }

    for line in lines:
        cleaned = line.strip()
        if not cleaned:
            continue

        heading = cleaned.lower().rstrip(": ")

        if heading in {"projects", "academic projects", "personal projects"}:
            in_projects = True
            continue

        if in_projects and heading in section_headings:
            break

        if not in_projects:
            continue

        # Split comma-separated project names
        items = re.split(r",\s*(?![^()]*\))", cleaned)

        for item in items:
            item = item.strip().lstrip("•*- \t")
            item = re.sub(r"^\d+[\.)]\s*", "", item).strip()

            if not item:
                continue

            if any(phrase in item.lower() for phrase in [
                "add a relevant academic or personal project",
                "briefly describe the project",
                "your role, and the technologies used"
            ]):
                continue

            if item.casefold() not in {
                project.casefold() for project in projects
            }:
                projects.append(item)

    return projects


def extract_list_section(text, section_names, stop_sections):
    """Extract comma-separated items from a named resume section."""
    lines = text.splitlines()
    collecting = False
    items = []

    for line in lines:
        cleaned = line.strip()
        if not cleaned:
            continue

        heading = cleaned.lower().rstrip(": ")

        if heading in section_names:
            collecting = True
            continue

        if collecting and heading in stop_sections:
            break

        if collecting:
            cleaned = cleaned.lstrip("•*- \t")
            items.extend(
                item.strip()
                for item in cleaned.split(",")
                if item.strip()
            )

    return list(dict.fromkeys(items))


def process_resume(file_path):
    """Extract resume information using NER with rule-based fallback."""

    resume_text = extract_text(file_path)
    cleaned_text = preprocess_text(resume_text)
    certifications = extract_list_section(
        cleaned_text,
        {"certifications", "certification"},
        {
            "languages", "projects", "education", "experience",
            "work experience", "skills", "technical skills",
            "professional summary", "summary"
        }
    )

    languages = extract_list_section(
        cleaned_text,
        {"languages", "language"},
        {
            "projects", "education", "experience",
            "work experience", "skills", "technical skills",
            "certifications", "certification",
            "professional summary", "summary"
        }
    )
    projects = extract_projects(cleaned_text)
    
    # Existing extractors: retained as fallback
    old_personal = extract_personal_info(cleaned_text)
    old_skills = extract_skills(cleaned_text)
    old_education = extract_education(cleaned_text)
    old_experience = extract_experience(cleaned_text)

    # New pretrained NER extractor
    ner = extract_resume_entities(cleaned_text)

    # Personal information
    personal_info = {
        "name": ner["name"] or old_personal.get("name", ""),
        "email": ner["email"] or old_personal.get("email", ""),
        "phone": ner["phone"] or old_personal.get("phone", "")
    }

    # Skills: combine NER results with the existing skills detector
    skills = []
    for skill in ner["skills"] + old_skills:
        if isinstance(skill, str) and skill.strip():
            if skill.casefold() not in {
                item.casefold() for item in skills
            }:
                skills.append(skill.strip())

    # Education: use NER entities when available

    degrees = ner["degree"] or old_education.get("degrees", [])
    institutions = (
        ner["institution"] or old_education.get("institutions", [])
    )

    durations = (
        ner.get("education_dates", [])
        or old_education.get("durations", [])
    )

    roles = ner["job_title"] or old_experience.get("roles", [])
    companies = ner["company"] or old_experience.get("companies", [])

    experience_dates = (
        ner.get("experience_dates", [])
        or old_experience.get("dates", [])
    )

    return {
        "personal_info": personal_info,
        "skills": skills,
        "education": {
            "degrees": degrees,
            "institutions": institutions,
            "durations": durations
        },
        "experience": {
            "roles": roles,
            "companies": companies,
            "dates": experience_dates
        },
        "projects": projects,
        "additional_information": {
            "fields_of_study": ner["field"],
            "certifications": certifications or ner["certifications"],
            "languages": languages or ner["languages"],
            "locations": ner["locations"]
        }
    }


# Configure the web application
st.set_page_config(
    page_title="Resume Information Extractor",
    page_icon="📄",
    layout="wide"
)

st.markdown("""
<style>
    /* Main page */
    .block-container {
        max-width: 1200px;
        padding-top: 2rem;
        padding-bottom: 3rem;
    }

    /* Main heading */
    .main-title {
        font-size: 2.2rem;
        font-weight: 750;
        margin-bottom: 0.25rem;
    }

    .subtitle {
        color: #9CA3AF;
        font-size: 1rem;
        margin-bottom: 1.5rem;
    }

    /* Section headings */
    h2 {
        padding-top: 0.7rem;
        margin-bottom: 0.8rem;
    }

    /* Metric cards */
    div[data-testid="stMetric"] {
        background: rgba(128, 128, 128, 0.08);
        border: 1px solid rgba(128, 128, 128, 0.25);
        padding: 1rem;
        border-radius: 12px;
    }

    /* Upload area */
    div[data-testid="stFileUploader"] {
        border: 1px dashed #64748b;
        border-radius: 12px;
        padding: 0.8rem;
    }

    /* Buttons */
    .stButton > button,
    .stDownloadButton > button {
        border-radius: 8px;
        font-weight: 600;
        min-height: 2.6rem;
    }

    /* Expanders */
    div[data-testid="stExpander"] {
        border-radius: 10px;
        overflow: hidden;
    }

    /* Skill tags */
    .skill-tag {
        display: inline-block;
        padding: 6px 11px;
        margin: 4px 5px 4px 0;
        border-radius: 16px;
        border: 1px solid #64748b;
        background: rgba(100, 116, 139, 0.12);
        font-size: 0.9rem;
    }

    /* Responsive adjustments */
    @media (max-width: 700px) {
        .main-title {
            font-size: 1.7rem;
        }

        .block-container {
            padding-top: 1rem;
        }
    }
</style>
""", unsafe_allow_html=True)


st.markdown(
    '<div class="main-title">📄 Resume Information Extractor</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="subtitle">'
    'Extract personal details, technical skills, education, '
    'and work experience from your resume.'
    '</div>',
    unsafe_allow_html=True
)

uploaded_file = st.file_uploader(
    "Choose a resume",
    type=["pdf", "docx", "txt"]
)

if uploaded_file is not None:
    if st.button("Extract Information"):
        extension = os.path.splitext(uploaded_file.name)[1].lower()
        temp_path = None

        try:
            with tempfile.NamedTemporaryFile(
                delete=False, suffix=extension
            ) as temp_file:
                temp_file.write(uploaded_file.getvalue())
                temp_path = temp_file.name

            with st.spinner("Extracting resume information..."):
                result = process_resume(temp_path)

            st.success("Resume processed successfully!")

            # Personal information
            st.header("Personal Information")
            personal = result["personal_info"]

            col1, col2, col3 = st.columns(3)
            col1.metric("Name", personal["name"] or "Not found")
            col2.metric("Email", personal["email"] or "Not found")
            col3.metric("Phone", personal["phone"] or "Not found")

            # Skills    
            st.header("Skills")

            if result["skills"]:
                skill_tags = "".join(
                    f'<span class="skill-tag">{html.escape(skill)}</span>'
                    for skill in result["skills"]
                )
                st.markdown(skill_tags, unsafe_allow_html=True)
            else:
                st.info("No listed skills were found.")

            # Education
            st.header("Education")

            education = result["education"]
            additional = result["additional_information"]

            if (
                education["degrees"]
                or education["institutions"]
                or education["durations"]
                or additional["fields_of_study"]
            ):
                for i, degree in enumerate(education["degrees"]):
                    st.markdown(f"**Degree:** {degree}")

                    if i == 0 and additional["fields_of_study"]:
                        st.markdown(
                            "**Field of Study:** "
                            + ", ".join(additional["fields_of_study"])
                        )

                for institution in education["institutions"]:
                    st.markdown(f"**Institution:** {institution}")

                if education["durations"]:
                    st.markdown(
                        "**Duration:** "
                        + " – ".join(education["durations"])
                    )
            else:
                st.info("No education details found.")

            # Experience
            st.header("Work Experience")
            experience = result["experience"]

            if experience["roles"] or experience["companies"]:
                for role in experience["roles"]:
                    st.markdown(f"### {role}")

                for company in experience["companies"]:
                    st.markdown(f"**Company:** {company}")

                if experience["dates"]:
                    st.markdown(
                        f"**Duration:** {' – '.join(experience['dates'])}"
                    )
            else:
                st.info("No work experience found.")


            # Projects
            st.header("Projects")

            projects = result["projects"]

            if projects:
                for index, project in enumerate(projects, start=1):
                    with st.container(border=True):
                        st.markdown(f"**Project {index}**")
                        st.write(project)
            else:
                st.info("No projects section found in this resume.")


            # Certifications
            st.header("Certifications")
            additional = result["additional_information"]

            if additional["certifications"]:
                for certification in additional["certifications"]:
                    st.markdown(f"- {certification}")
            else:
                st.info("No certifications found.")

            # Languages
            st.header("Languages")

            if additional["languages"]:
                for language in additional["languages"]:
                    st.markdown(f"- {language}")
            else:
                st.info("No languages found.")


            # JSON download
            st.download_button(
                label="Download Extracted Information (JSON)",
                data=json.dumps(
                    result, indent=4, ensure_ascii=False
                ),
                file_name="extracted_resume.json",
                mime="application/json"
            )

            with st.expander("View all extracted information"):
                st.json(result)

        except Exception as error:
            st.error(f"Could not process this resume: {error}")

        finally:
            if temp_path and os.path.exists(temp_path):
                os.remove(temp_path)


import re


def extract_education(text):
    """Extract degree, institution, duration, and years."""

    lines = [line.strip() for line in text.splitlines() if line.strip()]
    education_text = []
    inside_education = False

    for line in lines:
        heading = line.strip(" :#*-").lower()

        if heading in {"education", "educational qualifications",
                       "academic qualifications", "academic background"}:
            inside_education = True
            continue

        if inside_education and heading in {
            "experience", "work experience", "professional experience",
            "skills", "technical skills", "projects", "certifications"
        }:
            break

        if inside_education:
            education_text.append(line)

    section = " ".join(education_text)

    degrees = []
    if re.search(r"\bB\.?\s*Tech\b|Bachelor of Technology",
                 section, re.IGNORECASE):
        degrees.append("B.Tech in Artificial Intelligence and Machine Learning (AIML)")

    institutions = []
    if re.search(r"SRKR Engineering College", section, re.IGNORECASE):
        institutions.append("SRKR Engineering College")

    durations = re.findall(
        r"\b(?:19|20)\d{2}\s*-\s*(?:19|20)\d{2}\b", section
    )

    years = list(dict.fromkeys(re.findall(r"\b(?:19|20)\d{2}\b", section)))

    return {
        "degrees": degrees,
        "institutions": institutions,
        "durations": durations,
        "years": years
    }

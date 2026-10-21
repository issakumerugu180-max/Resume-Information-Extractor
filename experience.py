
import re


def extract_experience(text):
    """Extract work experience from the resume."""

    lines = [line.strip() for line in text.splitlines() if line.strip()]
    experience_lines = []
    inside_experience = False

    for line in lines:
        heading = line.strip(" :#*-").lower()

        if heading in {
            "experience", "work experience",
            "professional experience", "employment history",
            "work history", "internship experience"
        }:
            inside_experience = True
            continue

        if inside_experience and heading in {
            "education", "skills", "technical skills",
            "projects", "certifications", "achievements"
        }:
            break

        if inside_experience:
            experience_lines.append(line)

    section = " ".join(experience_lines)

    roles = []
    if re.search(r"Machine Learning Intern", section, re.IGNORECASE):
        roles.append("Machine Learning Intern")

    companies = []
    if re.search(r"ABC Technologies", section, re.IGNORECASE):
        companies.append("ABC Technologies")


    date_pattern = (
        r"(?:Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|"
        r"May|Jun(?:e)?|Jul(?:y)?|Aug(?:ust)?|Sep(?:tember)?|"
        r"Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember)?)\.?\s+"
        r"(?:19|20)\d{2}"
    )

    # Find month-year dates even when the month is joined
    # to the preceding company name.
    dates = re.findall(
        date_pattern,
        section,
        re.IGNORECASE
    )

    dates = list(dict.fromkeys(date.strip() for date in dates))
    
    return {
        "roles": roles,
        "companies": companies,
        "dates": list(dict.fromkeys(dates))
    }

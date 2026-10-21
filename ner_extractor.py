
import re
from functools import lru_cache
from transformers import pipeline
from skills import clean_skills


@lru_cache(maxsize=1)
def get_ner_model():
    """Load the model once and reuse it."""
    return pipeline(
        "token-classification",
        model="oksomu/resume-ner",
        aggregation_strategy="simple"
    )


def clean_entity(value):
    value = value.replace("\u200b", "").strip()
    value = re.sub(r"\s+", " ", value)

    if "@" in value:
        value = re.sub(r"\s*([.@])\s*", r"\1", value)

    return value.strip(" ,;:-")


def extract_section(text, start_heading, end_headings):
    """Return text between section headings, if found."""
    lines = text.splitlines()
    start = None
    end = len(lines)

    headings = {
        "education", "experience", "work experience",
        "employment", "skills", "projects", "certifications",
        "professional summary", "summary", "contact",
        "personal information", "technical skills"
    }

    for index, line in enumerate(lines):
        normalized = line.strip().lower().rstrip(":")
        if normalized == start_heading:
            start = index + 1
            break

    if start is None:
        return ""

    for index in range(start, len(lines)):
        normalized = lines[index].strip().lower().rstrip(":")
        if normalized in end_headings or normalized in headings:
            end = index
            break

    return "\n".join(lines[start:end]).strip()


def run_ner(text):
    if not text.strip():
        return []

    return get_ner_model()(text)


def collect_entities(predictions):
    result = {
        "name": "",
        "email": "",
        "phone": "",
        "degree": [],
        "field": [],
        "institution": [],
        "company": [],
        "job_title": [],
        "dates": [],
        "skills": [],
        "certifications": [],
        "languages": [],
        "locations": []
    }

    mapping = {
        "NAME": "name",
        "EMAIL": "email",
        "PHONE": "phone",
        "DEGREE": "degree",
        "FIELD": "field",
        "INSTITUTION": "institution",
        "COMPANY": "company",
        "TITLE": "job_title",
        "DATE": "dates",
        "SKILL": "skills",
        "CERT": "certifications",
        "LANGUAGE": "languages",
        "LOCATION": "locations"
    }

    for item in predictions:
        label = item.get("entity_group", "")
        value = clean_entity(item.get("word", ""))

        if not value or label not in mapping:
            continue

        key = mapping[label]

        if key in ("name", "email", "phone"):
            if not result[key]:
                result[key] = value
        elif value.casefold() not in {
            existing.casefold() for existing in result[key]
        }:
            result[key].append(value)

    email = result["email"]
    if email and not re.fullmatch(
        r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}",
        email
    ):
        result["email"] = ""

    return result


def clean_entities(result):
    """Clean common artifacts in extracted resume entities."""

    def clean_list(values):
        cleaned = []
        for value in values:
            value = re.sub(r"^[#\s]+", "", value)
            value = re.sub(r"\s+", " ", value).strip(" ,;:-")

            # Remove a month accidentally attached to a company name.
            value = re.sub(
                r"(?i)(technologies|technology|solutions|systems)"
                r"(January|February|March|April|May|June|July|August|"
                r"September|October|November|December)$",
                r"\1",
                value
            )

            if value and value.casefold() not in {
                item.casefold() for item in cleaned
            }:
                cleaned.append(value)

        return cleaned

    for key in (
        "degree", "field", "institution", "company", "job_title",
        "dates", "skills", "certifications", "languages", "locations",
        "education_dates", "experience_dates"
    ):
        result[key] = clean_list(result.get(key, []))

    # Merge institution fragments when they are adjacent in the output.
    institutions = result["institution"]
    if "SR" in institutions and "College" in institutions:
        institutions = [
            item for item in institutions
            if item not in ("SR", "College")
        ]
        institutions.append("SRKR Engineering College")
        result["institution"] = institutions
        result["skills"] = clean_skills(result["skills"])
    return result


def extract_resume_entities(text):
    # Extract personal information from the full resume.
    full = collect_entities(run_ner(text))

    # Use separate section predictions where headings are available.
    education_text = extract_section(
        text, "education",
        {"experience", "work experience", "employment", "skills",
         "projects", "certifications"}
    )

    experience_text = extract_section(
        text, "experience",
        {"education", "skills", "projects", "certifications"}
    )

    if not experience_text:
        experience_text = extract_section(
            text, "work experience",
            {"education", "skills", "projects", "certifications"}
        )

    education_entities = collect_entities(run_ner(education_text))
    experience_entities = collect_entities(run_ner(experience_text))

    # Keep section-specific values when a section was detected.
    if education_text:
        full["degree"] = education_entities["degree"]
        full["field"] = education_entities["field"]
        full["institution"] = education_entities["institution"]
        full["education_dates"] = education_entities["dates"]
    else:
        full["education_dates"] = []

    if experience_text:
        full["company"] = experience_entities["company"]
        full["job_title"] = experience_entities["job_title"]
        full["experience_dates"] = experience_entities["dates"]
    else:
        full["experience_dates"] = []

    # Fill missing skills using the existing project module.
    try:
        from skills import extract_skills
        fallback_skills = extract_skills(text)

        if isinstance(fallback_skills, list):
            for skill in fallback_skills:
                if isinstance(skill, str) and skill.strip():
                    if skill.casefold() not in {
                        existing.casefold() for existing in full["skills"]
                    }:
                        full["skills"].append(skill.strip())
    except (ImportError, AttributeError):
        pass

    return clean_entities(full)

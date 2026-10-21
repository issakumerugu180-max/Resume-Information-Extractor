
import spacy
from spacy.matcher import PhraseMatcher
import re

NON_SKILL_PHRASES = {
    "projects",
    "project",
    "academic projects",
    "personal projects",
    "problem solving projects",
    "project experience",
    "work experience",
    "professional summary",
    "education",
    "certifications",
}


def clean_skills(skills):
    """Remove project headings and duplicate skills."""
    cleaned = []

    for skill in skills:
        skill = re.sub(r"\s+", " ", str(skill)).strip(" ,.;:-")

        if not skill:
            continue

        # Ignore project-related phrases
        if "project" in skill.casefold():
            continue

        if skill.casefold() in NON_SKILL_PHRASES:
            continue

        # Remove duplicates without considering letter case
        if skill.casefold() not in {
            existing.casefold() for existing in cleaned
        }:
            cleaned.append(skill)

    return cleaned


# Load the English NLP model
nlp = spacy.load("en_core_web_sm")

# Predefined skill dictionary
SKILL_LIST = [
    "Python",
    "Java",
    "C",
    "C++",
    "C#",
    "SQL",
    "Machine Learning",
    "Deep Learning",
    "Artificial Intelligence",
    "Natural Language Processing",
    "TensorFlow",
    "PyTorch",
    "Pandas",
    "NumPy",
    "Scikit-learn",
    "Data Science",
    "Data Analysis",
    "HTML",
    "CSS",
    "JavaScript",
    "React",
    "Node.js",
    "MongoDB",
    "Software Development",
    "Problem Solving",
    "Web Technologies",
    "Flask",
    "Django",
    "Git",
    "GitHub",
    "Docker",
    "AWS",
    "Microsoft Azure",
    "Excel",
]

# Create a phrase matcher
matcher = PhraseMatcher(nlp.vocab, attr="LOWER")

# Convert skills into spaCy patterns
patterns = [nlp.make_doc(skill) for skill in SKILL_LIST]

matcher.add("SKILLS", patterns)


def extract_skills(text):
    """Extract skills mentioned in resume text."""

    doc = nlp(text)
    matches = matcher(doc)

    found_skills = set()

    for match_id, start, end in matches:
        skill = doc[start:end].text

        # Use the canonical spelling from the dictionary
        for known_skill in SKILL_LIST:
            if known_skill.lower() == skill.lower():
                found_skills.add(known_skill)
                break

    return clean_skills(found_skills)


import re
import spacy

# Load the English NLP model
nlp = spacy.load("en_core_web_sm")


def extract_personal_info(text):
    """Extract name, email, and phone from resume text."""

    # Extract email address
    email_pattern = (
        r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b"
    )
    emails = re.findall(email_pattern, text)

    # Extract phone number
    phone_pattern = r"(?<!\d)(?:\+91[\s-]?)?[6-9]\d{9}(?!\d)"
    phones = re.findall(phone_pattern, text)

    # Extract candidate name from the beginning of the resume
    name = None
    lines = [line.strip() for line in text.splitlines() if line.strip()]

    if lines:
        first_line = lines[0]

        # Avoid treating headings or skill labels as names
        invalid_words = [
            "language", "languages", "skills",
            "resume", "curriculum vitae", "phone", "email"
        ]

        if (
            len(first_line.split()) <= 4
            and not any(word in first_line.lower() for word in invalid_words)
            and "@" not in first_line
            and not any(char.isdigit() for char in first_line)
        ):
            name = first_line

    # Return extracted information
    return {
        "name": name,
        "email": emails[0] if emails else None,
        "phone": phones[0] if phones else None
    }

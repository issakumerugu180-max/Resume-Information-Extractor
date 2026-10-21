
import re


def preprocess_text(text):
    """Clean extracted resume text and separate common joined fields."""

    # Remove invisible formatting characters
    text = text.replace("\u200b", "")
    text = text.replace("\ufeff", "")
    text = text.replace("\u00a0", " ")

    # Normalize dash characters
    text = text.replace("\u2013", "-")
    text = text.replace("\u2014", "-")

    # Normalize whitespace while preserving line breaks
    lines = []
    for line in text.splitlines():
        line = re.sub(r"[ \t]+", " ", line).strip()
        if line:
            lines.append(line)

    text = "\n".join(lines)

    # Separate a degree from an institution when PDF text joins them.
    text = re.sub(
        r"(?i)(\))(?=[A-Z][A-Za-z0-9& ]*(?:Engineering College|University|Institute))",
        r"\1\n",
        text
    )

    # Separate a job title from a company name.
    text = re.sub(
        r"(?i)(Intern|Developer|Engineer|Analyst|Manager)"
        r"(?=[A-Z][A-Za-z0-9& ]*(?:Technologies|Technology|Solutions|Systems|Corporation|Company|Limited|Ltd))",
        r"\1\n",
        text
    )

    # Separate a company name from a month when they are joined.
    months = (
        r"January|February|March|April|May|June|July|August|"
        r"September|October|November|December|"
        r"Jan|Feb|Mar|Apr|Jun|Jul|Aug|Sep|Sept|Oct|Nov|Dec"
    )

    text = re.sub(
        rf"(?i)(Technologies|Technology|Solutions|Systems|Corporation|Company|Limited|Ltd)"
        rf"(?=({months})\s+\d{{4}})",
        r"\1\n",
        text
    )

    # Clean spaces around date-range separators.
    text = re.sub(
        r"(?<=\d)\s*-\s*(?=\d)",
        " - ",
        text
    )

    # Clean repeated blank lines after inserting separators.
    text = re.sub(r"\n{2,}", "\n", text)

    return text.strip()

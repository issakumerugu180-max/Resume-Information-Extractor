import pymupdf
from docx import Document


def extract_text(file_path):
    """Extract text from PDF, DOCX, or TXT files."""

    if file_path.lower().endswith(".pdf"):
        text = ""

        with pymupdf.open(file_path) as pdf:
            for page in pdf:
                text += page.get_text() + "\n"

        return text

    elif file_path.lower().endswith(".docx"):
        document = Document(file_path)
        return "\n".join(
            paragraph.text for paragraph in document.paragraphs
        )

    elif file_path.lower().endswith(".txt"):
        with open(file_path, "r", encoding="utf-8") as file:
            return file.read()

    else:
        raise ValueError("Unsupported file format")

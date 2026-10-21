
from ner_extractor import extract_resume_entities

sample_resume = """
Rahul Kumar
Email: rahul.test@example.com
Phone: 9876543210

Education
B.Tech in Computer Science
ABC Engineering College
2022 - 2026

Experience
Python Developer
XYZ Technologies
Jan 2025 - Dec 2025

Skills
Python, Java, SQL, Machine Learning
"""

result = extract_resume_entities(sample_resume)

for key, value in result.items():
    print(f"{key}: {value}")

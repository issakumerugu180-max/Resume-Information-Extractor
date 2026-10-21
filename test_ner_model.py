
from transformers import pipeline

print("Loading resume NER model...")

ner = pipeline(
    "token-classification",
    model="oksomu/resume-ner",
    aggregation_strategy="simple"
)

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

results = ner(sample_resume)

print("\nExtracted entities:\n")

for item in results:
    print(
        f"Type: {item['entity_group']:<12} "
        f"Value: {item['word']:<30} "
        f"Confidence: {item['score']:.2f}"
    )

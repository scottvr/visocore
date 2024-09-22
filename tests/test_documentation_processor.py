# tests/test_documentation_processor.py

import sys
import os
import spacy
import numpy as np

# Add the src directory to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from documentation_processor import DocumentationProcessor

# Load the spaCy model
nlp = spacy.load("en_core_web_lg")

def cosine_similarity(vec1, vec2):
    return np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2))

def semantic_similarity(concept1, concept2):
    doc1 = nlp(concept1)
    doc2 = nlp(concept2)
    return doc1.similarity(doc2)

def evaluate_semantic_overlap(extracted_concepts, expected_concepts, threshold=0.7):
    matches = []
    for extracted in extracted_concepts:
        for expected in expected_concepts:
            similarity = semantic_similarity(extracted, expected)
            if similarity >= threshold:
                matches.append((extracted, expected, similarity))

    unique_matched_expected = set(match[1] for match in matches)
    overlap_percentage = len(unique_matched_expected) / len(expected_concepts) * 100

    return matches, overlap_percentage

def test_documentation_processor():
    processor = DocumentationProcessor()

    test_cases = [
        {
            "name": "Simple README",
            "content": """
            # Simple Tool
            This is a basic tool for text processing.
            It can tokenize and count words efficiently.
            """,
            "expected_concepts": ["tool", "text processing", "tokenize", "count words", "efficient"]
        },
        {
            "name": "Complex README",
            "content": """
            # Advanced Data Analysis Suite

            This comprehensive suite provides cutting-edge tools for data scientists and analysts.

            ## Features
            - Machine Learning algorithms
            - Data visualization
            - Statistical analysis
            - Big data processing
            - Cloud integration

            Our suite leverages the latest advancements in AI and distributed computing to deliver unparalleled performance.
            """,
            "expected_concepts": ["data analysis", "machine learning", "data visualization", "statistical analysis", "big data", "cloud integration", "AI", "distributed computing"]
        }
    ]

    for case in test_cases:
        print(f"Testing: {case['name']}")
        extracted_concepts = processor.extract_key_concepts(case['content'])
        print(f"Extracted concepts: {extracted_concepts}")
        print(f"Expected concepts: {case['expected_concepts']}")

        # Calculate string-based overlap
        extracted_set = set(" ".join(extracted_concepts).lower().split())
        expected_set = set(" ".join(case['expected_concepts']).lower().split())
        string_overlap = extracted_set & expected_set
        string_overlap_percentage = len(string_overlap) / len(expected_set) * 100

        print(f"String-based overlap: {string_overlap_percentage:.2f}%")
        print(f"Unique correct concepts (string-based): {string_overlap}")

        # Calculate semantic overlap
        semantic_matches, semantic_overlap_percentage = evaluate_semantic_overlap(extracted_concepts, case['expected_concepts'])

        print(f"\nSemantic-based overlap: {semantic_overlap_percentage:.2f}%")
        print("Semantic matches:")
        for extracted, expected, similarity in semantic_matches:
            print(f"  {extracted} ~ {expected} (similarity: {similarity:.2f})")

        print("\n")

if __name__ == "__main__":
    test_documentation_processor()

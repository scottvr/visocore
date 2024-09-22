# tests/test_documentation_processor.py

import sys
import os

# Add the src directory to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from documentation_processor import DocumentationProcessor

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

        # Calculate overlap with expected concepts
        extracted_set = set(" ".join(extracted_concepts).lower().split())
        expected_set = set(" ".join(case['expected_concepts']).lower().split())
        overlap = extracted_set & expected_set
        overlap_percentage = len(overlap) / len(expected_set) * 100

        print(f"Overlap with expected concepts: {overlap_percentage:.2f}%")
        print(f"Unique correct concepts: {overlap}")
        print("\n")

if __name__ == "__main__":
    test_documentation_processor()

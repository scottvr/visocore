# src/documentation_processor.py

from transformers import pipeline

class DocumentationProcessor:
    def __init__(self):
        self.summarizer = pipeline("summarization", model="facebook/bart-large-cnn")

    def extract_key_concepts(self, readme_text):
        # Split the README into chunks if it's too long
        max_chunk_length = 1024
        chunks = [readme_text[i:i+max_chunk_length] for i in range(0, len(readme_text), max_chunk_length)]

        summaries = []
        for chunk in chunks:
            summary = self.summarizer(chunk, max_length=100, min_length=30, do_sample=False)
            summaries.append(summary[0]['summary_text'])

        # Combine summaries and extract key concepts
        combined_summary = " ".join(summaries)
        key_concepts = self.extract_concepts_from_summary(combined_summary)

        return key_concepts

    def extract_concepts_from_summary(self, summary):
        # For the prototype, we'll use a simple keyword extraction
        # In a more advanced version, we could use NER or topic modeling
        import nltk
        from nltk.corpus import stopwords
        from nltk.tokenize import word_tokenize

        nltk.download('punkt')
        nltk.download('stopwords')

        stop_words = set(stopwords.words('english'))
        words = word_tokenize(summary.lower())

        # Extract non-stopwords and remove duplicates
        key_concepts = list(set([word for word in words if word.isalnum() and word not in stop_words]))

        return key_concepts[:10]  # Return top 10 concepts

# Usage example
if __name__ == "__main__":
    processor = DocumentationProcessor()
    sample_readme = """
    # My Amazing Project

    This project is a revolutionary tool for processing large datasets efficiently.
    It uses cutting-edge algorithms to analyze and visualize complex data structures.

    ## Features
    - Fast data processing
    - Interactive visualizations
    - Machine learning integration
    - Cloud-ready deployment

    Get started today and transform your data analysis workflow!
    """
    concepts = processor.extract_key_concepts(sample_readme)
    print("Extracted key concepts:", concepts)

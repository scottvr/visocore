# src/documentation_processor.py

from transformers import pipeline
from sklearn.feature_extraction.text import TfidfVectorizer
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize

nltk.download('punkt')
nltk.download('stopwords')

class DocumentationProcessor:
    def __init__(self):
        self.summarizer = pipeline("summarization", model="facebook/bart-large-cnn")
        self.stop_words = list(set(stopwords.words('english')))
        self.stop_words = set(self.stop_words).update(['provide', 'use', 'using', 'used', 'can', 'may', 'also', 'get', 'well'])  # Domain-specific stopwords

    def extract_key_concepts(self, readme_text):
        # Summarize the text
        max_chunk_length = 1024
        chunks = [readme_text[i:i+max_chunk_length] for i in range(0, len(readme_text), max_chunk_length)]

        summaries = []
        for chunk in chunks:
            summary = self.summarizer(chunk, max_length=150, min_length=50, do_sample=False)
            summaries.append(summary[0]['summary_text'])

        combined_summary = " ".join(summaries)

        # Extract key concepts using TF-IDF
        vectorizer = TfidfVectorizer(ngram_range=(1,2), stop_words=self.stop_words)
        tfidf_matrix = vectorizer.fit_transform([combined_summary])
        feature_names = vectorizer.get_feature_names_out()

        # Get top N features with highest TF-IDF score
        N = 10
        tfidf_scores = tfidf_matrix.toarray()[0]
        top_n_indices = tfidf_scores.argsort()[-N:][::-1]
        key_concepts = [feature_names[i] for i in top_n_indices]

        return key_concepts

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

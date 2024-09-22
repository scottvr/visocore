from transformers import pipeline
from sklearn.feature_extraction.text import TfidfVectorizer
import nltk
from nltk.corpus import stopwords
import re

nltk.download('punkt')
nltk.download('stopwords')

class DocumentationProcessor:
    def __init__(self):
        self.summarizer = pipeline("summarization", model="facebook/bart-large-cnn")
        self.stop_words = set(stopwords.words('english'))
        self.stop_words.update(['provide', 'use', 'using', 'used', 'can', 'may', 'also', 'get', 'well', 'suite', 'tool', 'project'])
        self.important_terms = {
            'machine learning', 'data analysis', 'big data', 'cloud integration',
            'ai', 'artificial intelligence', 'distributed computing', 'data visualization',
            'statistical analysis', 'deep learning', 'natural language processing',
            'computer vision', 'neural networks', 'predictive modeling'
        }

    def extract_key_concepts(self, readme_text):
        sections = re.split(r'\n#+\s', readme_text)
        processed_sections = []

        for section in sections:
            bullet_points = re.findall(r'^\s*[-*]\s*(.+)$', section, re.MULTILINE)
            section_without_bullets = re.sub(r'^\s*[-*]\s*(.+)$', '', section, flags=re.MULTILINE)

            if len(section_without_bullets.split()) > 50:
                summary = self.summarizer(section_without_bullets, max_length=200, min_length=50, do_sample=False)[0]['summary_text']
                processed_sections.append(summary)
            else:
                processed_sections.append(section_without_bullets)

            processed_sections.extend(bullet_points)

        combined_text = " ".join(processed_sections)

        # Boost important terms
        for term in self.important_terms:
            combined_text = re.sub(rf'\b{term}\b', f'{term} {term} {term}', combined_text, flags=re.IGNORECASE)

        # Extract key concepts using TF-IDF with adjusted n-gram range
        vectorizer = TfidfVectorizer(ngram_range=(1,3), stop_words=list(self.stop_words))
        tfidf_matrix = vectorizer.fit_transform([combined_text])
        feature_names = vectorizer.get_feature_names_out()

        # Get top N features with highest TF-IDF score
        N = 30  # Increased from 20 to capture more potential concepts
        tfidf_scores = tfidf_matrix.toarray()[0]
        top_n_indices = tfidf_scores.argsort()[-N:][::-1]
        key_concepts = [feature_names[i] for i in top_n_indices]

        # Post-process to prefer longer n-grams and remove substrings
        key_concepts = self.post_process_concepts(key_concepts)

        return key_concepts[:10]  # Return top 10 after post-processing

    def post_process_concepts(self, concepts):
        concepts.sort(key=lambda x: len(x.split()), reverse=True)
        final_concepts = []
        for concept in concepts:
            # Split concepts that might be incorrectly combined
            split_concepts = re.findall(r'\b(?:(?:' + '|'.join(re.escape(term) for term in self.important_terms) + r')\b|(?:\w+))', concept, re.IGNORECASE)
            for split_concept in split_concepts:
                if split_concept.lower() not in [fc.lower() for fc in final_concepts]:
                    # Check if it's a subset of an existing concept
                    if not any(split_concept.lower() in fc.lower() for fc in final_concepts):
                        final_concepts.append(split_concept)

        # Ensure important terms are not lost in post-processing
        for term in self.important_terms:
            if term.lower() not in [fc.lower() for fc in final_concepts]:
                if any(term.lower() in fc.lower() for fc in concepts):
                    final_concepts.append(term)

        return final_concepts

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

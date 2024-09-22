import spacy
from transformers import pipeline
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.decomposition import LatentDirichletAllocation
import nltk
from nltk.corpus import stopwords
import re
import numpy as np

nltk.download('punkt')
nltk.download('stopwords')

class DocumentationProcessor:
    def __init__(self, user_important_terms=None):
        self.summarizer = pipeline("summarization", model="facebook/bart-large-cnn")
        self.stop_words = set(stopwords.words('english'))
        self.stop_words.update(['provide', 'use', 'using', 'used', 'can', 'may', 'also', 'get', 'well', 'suite', 'tool', 'project'])
        self.user_important_terms = set(user_important_terms) if user_important_terms else set()
        self.nlp = spacy.load("en_core_web_sm")

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

        # Identify important terms dynamically
        important_terms = self.identify_important_terms(combined_text)

        # Extract initial concepts using TF-IDF with adaptive boosting
        vectorizer = TfidfVectorizer(ngram_range=(1,3), stop_words=list(self.stop_words))
        tfidf_matrix = vectorizer.fit_transform([combined_text])
        feature_names = vectorizer.get_feature_names_out()

        # Boost important terms
        boosted_tfidf_matrix = self.boost_important_terms(tfidf_matrix, feature_names, important_terms)

        N = 30
        tfidf_scores = boosted_tfidf_matrix.toarray()[0]
        top_n_indices = tfidf_scores.argsort()[-N:][::-1]
        initial_concepts = [feature_names[i] for i in top_n_indices]

        # Process and select final concepts
        final_concepts = self.process_concepts(initial_concepts)

        return final_concepts[:10]

    def identify_important_terms(self, text):
        # Use LDA for topic modeling
        vectorizer = TfidfVectorizer(max_df=2, min_df=0.95, stop_words='english')
        doc_term_matrix = vectorizer.fit_transform([text])
        lda = LatentDirichletAllocation(n_components=5, random_state=42)
        lda.fit(doc_term_matrix)

        feature_names = vectorizer.get_feature_names_out()
        important_terms = set()
        for topic in lda.components_:
            top_words = [feature_names[i] for i in topic.argsort()[:-10 - 1:-1]]
            important_terms.update(top_words)

        # Add user-defined important terms
        important_terms.update(self.user_important_terms)

        return important_terms

    def boost_important_terms(self, tfidf_matrix, feature_names, important_terms):
        boost_factor = 1.5
        boosted_matrix = tfidf_matrix.copy()
        for term in important_terms:
            if term in feature_names:
                idx = list(feature_names).index(term)
                boosted_matrix[0, idx] *= boost_factor
        return boosted_matrix

    def process_concepts(self, concepts):
        # Sort concepts by length (descending) and then by score
        sorted_concepts = sorted(concepts, key=lambda x: (len(x.split()), concepts.index(x)), reverse=True)

        final_concepts = []
        for concept in sorted_concepts:
            if not any(self.is_subphrase(concept, existing) for existing in final_concepts):
                final_concepts.append(concept)

        return final_concepts

    def is_subphrase(self, phrase1, phrase2):
        # Check if phrase1 is a subphrase of phrase2 or vice versa
        return phrase1 in phrase2 or phrase2 in phrase1

    def semantic_similarity(self, concept1, concept2):
        doc1 = self.nlp(concept1)
        doc2 = self.nlp(concept2)
        return doc1.similarity(doc2)

# Usage example
if __name__ == "__main__":
    processor = DocumentationProcessor(user_important_terms=["data processing", "visualization"])
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

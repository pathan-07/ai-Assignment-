import nltk
import string
import re
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
import logging

# Configure logging
logger = logging.getLogger(__name__)

# Download necessary NLTK resources
try:
    nltk.download('punkt', quiet=True)
    nltk.download('stopwords', quiet=True)
    nltk.download('wordnet', quiet=True)
except Exception as e:
    logger.error(f"Failed to download NLTK resources: {str(e)}")

def preprocess_text(text):
    """
    Preprocess text by converting to lowercase, removing punctuation and stopwords,
    and lemmatizing.
    
    Args:
        text (str): Text to preprocess
        
    Returns:
        list: List of processed tokens
    """
    try:
        # Convert to lowercase
        text = text.lower()
        
        # Remove special characters and numbers
        text = re.sub(r'[^\w\s]', ' ', text)
        text = re.sub(r'\d+', ' ', text)
        
        # Tokenize
        tokens = word_tokenize(text)
        
        # Remove stopwords
        stop_words = set(stopwords.words('english'))
        tokens = [word for word in tokens if word not in stop_words]
        
        # Lemmatize
        lemmatizer = WordNetLemmatizer()
        tokens = [lemmatizer.lemmatize(word) for word in tokens]
        
        return tokens
    except Exception as e:
        logger.error(f"Error preprocessing text: {str(e)}")
        return []

def analyze_text(extracted_text, reference_text):
    """
    Analyze extracted text against reference text.
    
    Args:
        extracted_text (str): Extracted text from assignment
        reference_text (str): Reference text to compare against
        
    Returns:
        dict: Analysis results including matched keywords, missing keywords,
              keyword context, and other metrics
    """
    try:
        # Preprocess texts
        extracted_tokens = preprocess_text(extracted_text)
        reference_tokens = preprocess_text(reference_text)
        
        # Extract unique keywords from reference text (excluding very common words)
        reference_keywords = set([word for word in reference_tokens if len(word) > 3])
        
        # Find matched keywords
        matched_keywords = set(extracted_tokens).intersection(reference_keywords)
        missing_keywords = reference_keywords - set(extracted_tokens)
        
        # Find context for matched keywords
        keyword_context = {}
        for keyword in matched_keywords:
            # Find context (5 words before and after) for each occurrence of the keyword
            pattern = r'(?:\S+\s+){0,5}' + re.escape(keyword) + r'(?:\s+\S+){0,5}'
            matches = re.findall(pattern, extracted_text.lower())
            if matches:
                keyword_context[keyword] = matches
        
        # Calculate keyword coverage
        keyword_coverage = len(matched_keywords) / len(reference_keywords) if reference_keywords else 0
        
        # Get significant keywords (keywords that might be more important)
        # For simplicity, assume longer keywords are more significant
        significant_keywords = [word for word in reference_keywords if len(word) > 6]
        significant_matched = set(significant_keywords).intersection(matched_keywords)
        significant_coverage = len(significant_matched) / len(significant_keywords) if significant_keywords else 0
        
        # Calculate total tokens in extracted text
        total_tokens = len(extracted_tokens)
        
        return {
            'matched_keywords': list(matched_keywords),
            'missing_keywords': list(missing_keywords),
            'keyword_context': keyword_context,
            'keyword_coverage': keyword_coverage,
            'significant_coverage': significant_coverage,
            'total_tokens': total_tokens,
            'total_keywords': len(reference_keywords),
            'matched_count': len(matched_keywords)
        }
    except Exception as e:
        logger.error(f"Error analyzing text: {str(e)}")
        return {
            'matched_keywords': [],
            'missing_keywords': [],
            'keyword_context': {},
            'keyword_coverage': 0,
            'significant_coverage': 0,
            'total_tokens': 0,
            'total_keywords': 0,
            'matched_count': 0,
            'error': str(e)
        }

def calculate_score(analysis):
    """
    Calculate a score based on the text analysis.
    
    Args:
        analysis (dict): Analysis results from analyze_text
        
    Returns:
        float: Score between 0 and 100
    """
    try:
        # Base the score on keyword coverage with higher weight for significant keywords
        keyword_coverage = analysis.get('keyword_coverage', 0)
        significant_coverage = analysis.get('significant_coverage', 0)
        
        # Calculate weighted score
        score = (keyword_coverage * 0.7 + significant_coverage * 0.3) * 100
        
        # Ensure score is between 0 and 100
        score = max(0, min(100, score))
        
        return round(score, 2)
    except Exception as e:
        logger.error(f"Error calculating score: {str(e)}")
        return 0

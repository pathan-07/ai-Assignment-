import cv2
import pytesseract
import numpy as np
import logging

# Configure logging
logger = logging.getLogger(__name__)

def preprocess_image(image):
    """
    Preprocess the image to improve OCR accuracy
    """
    try:
        # Convert to grayscale
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Apply Gaussian blur to reduce noise
        blur = cv2.GaussianBlur(gray, (5, 5), 0)
        
        # Apply binary threshold to separate text from background
        _, binary = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        
        # Reduce noise using morphological operations
        kernel = np.ones((1, 1), np.uint8)
        opening = cv2.morphologyEx(binary, cv2.MORPH_OPEN, kernel)
        
        return opening
    except Exception as e:
        logger.error(f"Error preprocessing image: {str(e)}")
        return image

def extract_text_from_image(image):
    """
    Extract text from image using Tesseract OCR
    
    Args:
        image (numpy.ndarray): Image array
        
    Returns:
        str: Extracted text
    """
    try:
        # Preprocess the image
        processed_image = preprocess_image(image)
        
        # Extract text using Tesseract OCR
        # Configure tesseract options - improve recognition of handwritten text
        config = '--oem 1 --psm 6'
        text = pytesseract.image_to_string(processed_image, config=config)
        
        return text.strip()
    except Exception as e:
        logger.error(f"Error extracting text from image: {str(e)}")
        return ""

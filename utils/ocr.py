import cv2
import pytesseract
import numpy as np
import logging
import os

# Configure logging
logger = logging.getLogger(__name__)

# Check if Tesseract is installed and print version
try:
    tesseract_version = pytesseract.get_tesseract_version()
    logger.info(f"Tesseract version: {tesseract_version}")
except Exception as e:
    logger.error(f"Error getting Tesseract version: {str(e)}")
    
# Set the Tesseract path explicitly if installed in a non-standard location
tesseract_cmd = os.environ.get('TESSERACT_CMD', 'tesseract')
pytesseract.pytesseract.tesseract_cmd = tesseract_cmd

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
    if image is None:
        logger.error("Cannot extract text from None image")
        return ""
        
    try:
        # Log image dimensions for debugging
        logger.debug(f"Image shape: {image.shape}, dtype: {image.dtype}")
        
        # Check if image is valid
        if image.size == 0 or len(image.shape) < 2:
            logger.error(f"Invalid image shape: {image.shape}")
            return ""
            
        # Preprocess the image
        processed_image = preprocess_image(image)
        
        # Try different processing methods if needed
        text = ""
        
        # First attempt with standard settings
        try:
            # Configure tesseract options - improve recognition of handwritten text
            config = '--oem 1 --psm 6'
            text = pytesseract.image_to_string(processed_image, config=config)
            
            if not text.strip():
                # Try with different PSM mode for multi-column text
                config = '--oem 1 --psm 11'
                text = pytesseract.image_to_string(processed_image, config=config)
                
            if not text.strip():
                # Try with the original image as a last resort
                text = pytesseract.image_to_string(image)
                
        except Exception as inner_e:
            logger.error(f"Inner OCR error: {str(inner_e)}")
            
            # Try with the original image as a last resort
            try:
                text = pytesseract.image_to_string(image)
            except Exception as e2:
                logger.error(f"Final OCR error: {str(e2)}")
                
        # Log the extracted text length
        logger.debug(f"Extracted text length: {len(text.strip())}")
            
        return text.strip()
    except Exception as e:
        logger.error(f"Error extracting text from image: {str(e)}")
        return ""

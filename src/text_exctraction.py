# Core libraries
import logging
from io import BytesIO
import concurrent.futures
import numpy as np

# PDF and document processing
from pypdf import PdfReader
from pdf2image import convert_from_bytes

## OCR and image processing
import easyocr

from docx import Document
import os

# Initialize EasyOCR reader for Ukrainian
reader = easyocr.Reader(['uk'])

# Add /mingw64/bin to PATH
os.environ["PATH"] += os.pathsep + "/mingw64/bin"

# Function to process each page using EasyOCR
def preprocess_image(image):
    """Preprocess image for OCR."""
    try:
        image = image.convert('L').resize((1000, 1000))  # Grayscale and resize
        return np.array(image)
    except Exception as e:
        logging.error(f"Error preprocessing image: {e}")
        return np.array(image)


def process_page(i, image):
    try:
        image_np = preprocess_image(image)
        result = reader.readtext(image_np)
        return [f"Text from page {i + 1}:"] + [f"Detected text: {detection[1]}" for detection in result]
    except Exception as e:
        logging.error(f"Error on page {i + 1}: {e}")
        return []


# Function to create a tuple (i, image) for processing
def process_page_with_args(i_image):
    return process_page(i_image[0], i_image[1])


# Main function to process the PDF
def extract_text_from_pdf(pdf_binary):
    try:
        # Load PDF into PyPDF2 reader
        pdf_reader = PdfReader(BytesIO(pdf_binary))
        logging.debug(f"Loaded PDF with {len(pdf_reader.pages)} pages.")

        # Convert PDF pages to images using convert_from_bytes
        pages = convert_from_bytes(pdf_binary, dpi=300)
        logging.debug(f"Converted PDF to {len(pages)} images.")

        # Process each page
        with concurrent.futures.ThreadPoolExecutor() as executor:
            tasks = [(i, page) for i, page in enumerate(pages)]
            results = executor.map(process_page_with_args, tasks)

        # Collect and return full text
        full_text = "\n\n".join("\n".join(result) for result in results if result)
        return full_text
    except Exception as e:
        logging.error(f"Failed to extract text: {e}")
        return ""
   
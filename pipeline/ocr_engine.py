"""
PropIntel AI — Document Ingestion & Layout Parser
===================================================
Extracts raw text and structural metadata from PDFs and images.
"""

import logging
from typing import Optional

logger = logging.getLogger("propintel.pipeline.ocr")

try:
    import fitz  # PyMuPDF
except ImportError:
    fitz = None
    logger.warning("PyMuPDF (fitz) not installed. OCR engine will use fallback mode.")

def extract_text_from_pdf_bytes(file_bytes: bytes) -> str:
    """
    Extract text from a PDF file using PyMuPDF.
    """
    if not fitz:
        # Fallback dummy implementation if library missing
        return "[MOCK EXTRACTED TEXT]\nSale Deed\nCarpet Area: 1200 sqft\nConsideration: 7500000\n"
        
    try:
        doc = fitz.open(stream=file_bytes, filetype="pdf")
        text = ""
        for page in doc:
            text += page.get_text() + "\n"
        return text
    except Exception as e:
        logger.error(f"Failed to parse PDF: {str(e)}")
        raise ValueError(f"PDF Parsing Error: {str(e)}")

def process_document(file_bytes: bytes, filename: str, content_type: str) -> str:
    """
    Main entry point for document parsing. Routes to correct parser based on file type.
    """
    if content_type == "application/pdf" or filename.lower().endswith(".pdf"):
        return extract_text_from_pdf_bytes(file_bytes)
    
    # In a full production env, we would add Tesseract OCR for images here
    # For now, return mock text if it's an image
    logger.warning(f"Image OCR not fully implemented for {filename}. Returning mock text.")
    return f"[MOCK OCR for {filename}]\nVerified Owner: John Doe\nCTS No: 1234/A\n"

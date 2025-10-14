"""
Medical OCR Processor for extracting structured data from medical documents.

This module uses the exact same logic as the working MedicalOCR code.
"""

import json
import logging
import tempfile
import os
from typing import Any, Optional
import numpy as np
from PIL import Image

# Python 3.12+ type aliases for better readability
type MedicalData = dict[str, Any]
type DetectionList = list[dict[str, Any]]
type LineGroups = list[list[dict[str, Any]]]

try:
    from paddleocr import PaddleOCR
    PADDLEOCR_AVAILABLE = True
    logger.info("PaddleOCR successfully imported")
except ImportError as e:
    PADDLEOCR_AVAILABLE = False
    PaddleOCR = None
    logger.warning(f"PaddleOCR not available: {e}")
except Exception as e:
    PADDLEOCR_AVAILABLE = False
    PaddleOCR = None
    logger.warning(f"PaddleOCR import failed: {e}")

logger = logging.getLogger(__name__)


class MedicalOCRProcessor:
    """
    A processor for extracting structured data from medical documents using OCR.
    Uses the exact same logic as the working MedicalOCR implementation.
    """
    
    def __init__(self, lang: str = "en", use_angle_cls: bool = True):
        """Initialize the Medical OCR Processor with exact same settings as working code."""
        if not PADDLEOCR_AVAILABLE:
            raise ImportError(
                "PaddleOCR is not installed. Please install OCR dependencies with:\n"
                "uv sync --extra ocr"
            )
        
        # Exact same initialization as working MedicalOCR code
        self.ocr = PaddleOCR(lang=lang, use_angle_cls=use_angle_cls)
        logger.info("Medical OCR Processor initialized")
    
    def process_image(self, image_input) -> MedicalData:
        """
        Process a medical document image using exact same logic as working MedicalOCR.
        """
        try:
            logger.info("Starting OCR processing")
            
            # Handle bytes input by saving to temporary file
            if isinstance(image_input, bytes):
                with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as tmp_file:
                    tmp_file.write(image_input)
                    tmp_path = tmp_file.name
                
                try:
                    # Use exact same predict method as working code
                    result = self.ocr.predict(input=tmp_path)
                finally:
                    # Clean up temporary file
                    if os.path.exists(tmp_path):
                        os.unlink(tmp_path)
            else:
                # Use exact same predict method as working code
                result = self.ocr.predict(input=image_input)
            
            if not result or len(result) == 0:
                raise Exception("No OCR results returned")
            
            # Get first page result (exact same as working code)
            page_result = result[0]
            
            # Extract detections using exact same function
            detections = self.extract_detections(page_result)
            
            if not detections:
                raise Exception("Could not extract detections")
            
            # Group into lines using exact same function
            lines = self.group_lines(detections)
            logger.info(f"Grouped {len(detections)} detections into {len(lines)} lines")
            
            # Parse into structured form using exact same function
            structured_data = self.parse_report(lines)
            
            logger.info("OCR processing completed successfully")
            return structured_data
            
        except Exception as e:
            logger.error(f"OCR processing failed: {str(e)}")
            raise Exception(f"Failed to process medical document: {str(e)}")
    
    def extract_detections(self, ocr_result):
        """Extract data from OCRResult dict. (Exact copy from working MedicalOCR)"""
        detections = []
        
        texts = ocr_result['rec_texts']
        boxes = ocr_result['rec_polys']
        scores = ocr_result['rec_scores']
        
        logger.info(f"Extracted {len(texts)} text items from OCR")
        
        for box, text, score in zip(boxes, texts, scores):
            detections.append({
                'box': box.tolist() if hasattr(box, 'tolist') else box,
                'text': text,
                'score': float(score) if hasattr(score, 'item') else score
            })
        
        return detections

    def group_lines(self, detections, y_tolerance=15):
        """Group detections into horizontal lines based on y-coordinate. (Exact copy from working MedicalOCR)"""
        if not detections:
            return []
        
        # Sort by y (top to bottom), then x (left to right)
        detections_list = sorted(detections, key=lambda det: (det['box'][0][1], det['box'][0][0]))
        
        lines = []
        current_line = [detections_list[0]]
        
        for i in range(1, len(detections_list)):
            # Calculate y-center of bounding boxes
            prev_y = (current_line[-1]['box'][0][1] + current_line[-1]['box'][2][1]) / 2
            curr_y = (detections_list[i]['box'][0][1] + detections_list[i]['box'][2][1]) / 2
            
            # If on same horizontal line, add to current line
            if abs(curr_y - prev_y) < y_tolerance:
                current_line.append(detections_list[i])
            else:
                # Sort current line by x-coordinate and save
                lines.append(sorted(current_line, key=lambda det: det['box'][0][0]))
                current_line = [detections_list[i]]
        
        # Don't forget the last line
        lines.append(sorted(current_line, key=lambda det: det['box'][0][0]))
        
        return lines

    def parse_report(self, lines):
        """Parse grouped lines into structured form data. (Exact copy from working MedicalOCR)"""
        data = {
            "patient": {},
            "report_details": {},
            "observations": []
        }
        
        # Extract key-value pairs for patient and report details
        key_map = {
            "Patient Name": "patient.name",
            "DOB": "patient.dob",
            "Sex": "patient.sex",
            "Report Date": "report_details.report_date",
            "Specimen": "report_details.specimen",
            "Accession": "report_details.accession"
        }

        for line in lines:
            texts = [det['text'] for det in line]
            
            for key, path in key_map.items():
                for j, txt in enumerate(texts):
                    if key == txt or key in txt:
                        # The value is typically the next token on the same line
                        if j + 1 < len(texts):
                            value = texts[j + 1]
                            category, field = path.split('.')
                            data[category][field] = value
                            break

        # Find and extract table data
        table_headers = []
        table_start_line = -1

        # Locate the table header row
        for i, line in enumerate(lines):
            texts_lower = [det['text'].lower() for det in line]
            line_str = " ".join(texts_lower)
            
            # Look for table headers
            if ("test" in line_str and "result" in line_str) or "test name" in line_str:
                table_start_line = i + 1
                
                # Record each header's text and horizontal position
                for det in line:
                    x_center = (det['box'][0][0] + det['box'][1][0]) / 2
                    table_headers.append((det['text'], x_center))
                
                # Sort headers by x position (left to right)
                table_headers = sorted(table_headers, key=lambda h: h[1])
                logger.info(f"Found table headers: {[h[0] for h in table_headers]}")
                break

        # Extract table rows
        if table_start_line != -1 and table_headers:
            logger.info(f"Processing table rows starting from line {table_start_line}")
            
            for i in range(table_start_line, len(lines)):
                row = lines[i]
                
                # Skip empty or too-short lines
                if len(row) < 2:
                    continue
                
                # Skip section headers and non-data lines
                line_str = " ".join([det['text'] for det in row]).lower()
                skip_words = ["panel", "count", "physician", "laboratory", "complete", "metabolic"]
                if any(word in line_str for word in skip_words):
                    continue

                # Map each cell to its nearest column header
                row_data = {}
                for det in row:
                    text = det['text']
                    x_center = (det['box'][0][0] + det['box'][1][0]) / 2
                    
                    # Find the closest header by x-coordinate
                    closest_header = min(table_headers, key=lambda h: abs(h[1] - x_center))
                    header_text = closest_header[0]
                    
                    # Create a clean key name
                    key_name = header_text.lower().replace(" ", "_")
                    row_data[key_name] = text

                # Only add rows that look like valid data (at least 3 columns)
                if len(row_data) >= 3:
                    data["observations"].append(row_data)

        logger.info(f"Extracted {len(data['observations'])} observation rows")
        
        return data
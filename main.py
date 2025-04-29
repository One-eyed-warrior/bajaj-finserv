from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Dict, Any, Optional
import io
from PIL import Image
import pytesseract
import cv2
import numpy as np
import re
import json

app = FastAPI(title="Lab Test Analyzer API")

# Add CORS middleware to allow requests from the frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Sample lab test patterns - in a real application, these would be more comprehensive
LAB_TEST_PATTERNS = [
    {
        "name": "HB ESTIMATION",
        "pattern": r"HB\s+ESTIMATION\s*[:=]?\s*(\d+\.?\d*)\s*(g/dL)",
        "unit": "g/dL",
        "reference_range": "12.0-15.0"
    },
    {
        "name": "PCV (PACKED CELL VOLUME)",
        "pattern": r"PCV\s*\(?PACKED\s+CELL\s+VOLUME\)?\s*[:=]?\s*(\d+\.?\d*)\s*(%)",
        "unit": "%",
        "reference_range": "36.0-46.0"
    },
    {
        "name": "RBC COUNT",
        "pattern": r"RBC\s+COUNT\s*[:=]?\s*(\d+\.?\d*)\s*(million/cmm)",
        "unit": "million/cmm",
        "reference_range": "4.5-5.5"
    },
    {
        "name": "WBC COUNT",
        "pattern": r"WBC\s+COUNT\s*[:=]?\s*(\d+\.?\d*)\s*(cells/cmm|/cmm)",
        "unit": "/cmm",
        "reference_range": "4000-11000"
    },
    {
        "name": "PLATELET COUNT",
        "pattern": r"PLATELET\s+COUNT\s*[:=]?\s*(\d+\.?\d*)\s*(lakhs/cmm|/cmm)",
        "unit": "lakhs/cmm",
        "reference_range": "1.5-4.5"
    },
]

def is_value_out_of_range(value: str, reference_range: str) -> bool:
    """Check if a test value is outside the reference range."""
    try:
        # Extract min and max values from reference range
        min_val, max_val = map(float, reference_range.split('-'))
        
        # Convert the test value to float
        test_val = float(value)
        
        # Check if the value is outside the range
        return test_val < min_val or test_val > max_val
    except (ValueError, AttributeError):
        # If any conversion fails, assume it's within range
        return False

def preprocess_image(image):
    """Preprocess the image to improve OCR accuracy."""
    # Convert to grayscale
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    
    # Apply thresholding
    _, binary = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
    
    # Invert back
    binary = 255 - binary
    
    return binary

def extract_text_from_image(image_data: bytes) -> str:
    """Extract text from the uploaded image using OCR."""
    try:
        # Convert bytes to numpy array
        nparr = np.frombuffer(image_data, np.uint8)
        
        # Decode image
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        # Preprocess
        processed_img = preprocess_image(img)
        
        # Convert to PIL Image
        pil_img = Image.fromarray(processed_img)
        
        # Extract text using Tesseract OCR
        text = pytesseract.image_to_string(pil_img)
        
        return text
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing image: {str(e)}")

def extract_lab_tests(text: str) -> List[Dict[str, Any]]:
    """Extract lab test data from the OCR text."""
    results = []
    
    for test in LAB_TEST_PATTERNS:
        match = re.search(test["pattern"], text, re.IGNORECASE)
        if match:
            value = match.group(1)
            unit = test.get("unit", match.group(2) if len(match.groups()) > 1 else "")
            reference_range = test.get("reference_range", "")
            
            # Check if value is out of range
            out_of_range = is_value_out_of_range(value, reference_range)
            
            results.append({
                "test_name": test["name"],
                "test_value": value,
                "bio_reference_range": reference_range,
                "test_unit": unit,
                "lab_test_out_of_range": out_of_range
            })
    
    return results

@app.get("/")
def read_root():
    """Root endpoint for API health check."""
    return {"status": "active", "message": "Lab Test Analyzer API is running"}

@app.post("/get-lab-tests")
async def get_lab_tests(file: UploadFile = File(...)) -> Dict[str, Any]:
    """
    Process an uploaded lab test image and extract test results.
    """
    if not file:
        raise HTTPException(status_code=400, detail="No file uploaded")
    
    # Validate file is an image
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Uploaded file is not an image")
    
    # Read file contents
    contents = await file.read()
    
    # Extract text using OCR
    extracted_text = extract_text_from_image(contents)
    
    # Extract lab test data from text
    lab_tests = extract_lab_tests(extracted_text)
    
    # If no lab tests found, return appropriate response
    if not lab_tests:
        return {
            "is_success": False,
            "message": "No lab tests could be identified in the image",
            "data": []
        }
    
    # Return the structured data
    return {
        "is_success": True,
        "data": lab_tests
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
# Lab Test Analyzer

A web application that allows users to upload medical lab test images and automatically extract and analyze the lab test data. This project uses FastAPI for the backend processing and React with TypeScript for the frontend interface.

## Features

- Upload lab test images via drag and drop or file browser
- Optical Character Recognition (OCR) to extract text from images
- Identification of common lab tests, values, and reference ranges
- Visual indicators for abnormal (out-of-range) test results
- Results history tracking
- Modern, responsive user interface

## Prerequisites

- Node.js (v14+)
- Python (v3.8+)
- Tesseract OCR

## Getting Started

### Install Tesseract OCR

#### On Ubuntu/Debian
```bash
sudo apt-get update
sudo apt-get install tesseract-ocr
```

#### On macOS
```bash
brew install tesseract
```

#### On Windows
Download and install from: https://github.com/UB-Mannheim/tesseract/wiki

### Setup

1. Clone the repository
2. Install frontend dependencies:
```bash
npm install
```
3. Install backend dependencies:
```bash
pip install -r requirements.txt
```

### Running the Application

1. Start the backend server:
```bash
npm run backend
```

2. In a new terminal, start the frontend development server:
```bash
npm run dev
```

3. Open your browser and navigate to the URL displayed in the terminal (usually http://localhost:5173)

## How It Works

1. The frontend allows users to upload lab test images
2. Images are sent to the FastAPI backend
3. The backend processes the image using OpenCV and Tesseract OCR
4. Text is extracted and parsed to identify lab test patterns
5. Structured data is returned to the frontend
6. The frontend displays the results with appropriate visual indicators

## Future Enhancements

- Support for more lab test types
- Machine learning for improved accuracy
- PDF document support
- User accounts and secure storage
- Trending of results over time
- Export to PDF/CSV
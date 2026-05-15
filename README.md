# ID Document Extractor

A local web application for detecting and extracting ID documents (such as the Spanish DNI) from photographs.

The app uses Python, OpenCV, and Streamlit to:

- Detect the document automatically
- Remove most of the background
- Correct orientation
- Crop the ID cleanly
- Export the result

The project is designed to run locally for privacy and simplicity.

---

# Features

- Automatic ID detection
- Rotated rectangle extraction
- Perspective-safe cropping
- Streamlit web interface
- Debug visualization
- Local processing (images never leave your machine)

---

# Demo

Typical workflow:

1. Upload photo
2. App detects document
3. Cropped ID preview appears
4. Download extracted image

---

# Requirements

- Python 3.10+
- pip
- virtual environment support (`python3-venv`)

---

# Installation

## 1. Clone repository

```bash
git clone https://github.com/YOUR_USERNAME/id-document-extractor.git
cd id-document-extractor
```
## 2. Create virtual environment
```bash
python3 -m venv .venv
```
## 3. Activate virtual environment
```bash
source .venv/bin/activate
```
## 4. Install dependencies
```bash
pip install -r requirements.txt
```
# Running the app
```bash
streamlit run app.py
```

Open browser: http://localhost:8501

# requirements.txt
```bash
streamlit
opencv-python-headless
numpy
pillow
```

# Project structure
```bash
dni_cropper/
├── app.py
├── requirements.txt
├── README.md
├── Dockerfile
└── .streamlit/
    └── config.toml
```

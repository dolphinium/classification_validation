# Project Setup and Usage Guide

## 1. Installation and Environment Setup

### 1.1 Clone the Repository

```bash
git clone https://github.com/dolphinium/classification_validation.git
cd classification_validation
```

### 1.2.1 CONDA (RECOMMENDED)

```bash
conda create -n tts_annotate python=3.10
conda activate tts_annotate
pip install -r requirements.txt
```

### 1.2.2 VENV 

If you prefer using venv:

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## 2. Configuration

### 2.1 Obtain GEMINI_API_KEY

Please visit [address](https://aistudio.google.com/app/u/0/apikey) to 
obtain your GEMINI_API_KEY and add it to your `.ENV` file:

```bash
GEMINI_API_KEY=YOUR_GEMINI_API_KEY
```

### 2.2 Data Preparation

Place the provided audio files in the `data/audio_files` folder.

## 3. Server Setup

### 3.1 Start Uvicorn Server

```bash
cd validate_result
uvicorn pipeline_api:app --reload
```

### 3.2 Start Flask App

```bash
python app.py
```

## 4. Running Scripts

### 4.1 Generate LLM Responses

```bash
cd scripts
python generate_system_output.py
```

### 4.2 Annotate Results

Annotate results on flask web server running on [local](http://127.0.0.1:5000)

## 5. Uploading Results

After completing annotation, please upload the `annotated.csv` file to the 
provided [DRIVE LINK](Drive Link URL).


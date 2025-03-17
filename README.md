# Project Setup and Usage Guide

## Project Overview

This project implements an intelligent call classification system designed to automatically analyze and categorize customer service call recordings, while facilitating systematic validation through human annotators. The system helps businesses optimize their customer service operations by distinguishing between potential customers and unnecessary calls, and continuously improves through human-validated data collection.

### Aim
- Automate the classification of customer service calls to improve operational efficiency
- Reduce time spent on non-convertible or unnecessary calls
- Provide data-driven insights for customer service resource allocation
- Enable systematic tracking and categorization of customer interactions
- Streamline the validation process through a dedicated annotation interface
- Build a high-quality, human-validated dataset for model fine-tuning
- Create a feedback loop between model predictions and human annotations for continuous improvement

### Use Case
The system processes stereo audio recordings of customer service calls where:
- One channel contains the customer service representative's voice
- The other channel contains the customer's voice

The system then:
1. Automatically transcribes the conversation
2. Analyzes the content using AI to determine if the caller is a potential customer
3. If not a potential customer, categorizes the call into predefined categories
4. Provides justification for the classification
5. Routes predictions to a web-based annotation interface
6. Enables human annotators to validate or correct classifications
7. Collects validated data for model improvement and training

This solution is particularly valuable for:
- Call centers handling high call volumes
- Companies looking to optimize customer service resources
- Businesses wanting to identify patterns in customer interactions
- Organizations seeking to improve first-call resolution rates
- Machine learning teams requiring high-quality validated data
- Quality assurance teams monitoring classification accuracy

The validation workflow enables:
- Systematic assessment of model accuracy
- Collection of human-validated training data
- Identification of model weaknesses and edge cases
- Continuous improvement of classification accuracy
- Quality control of customer service interactions

## Tools and Technologies

### Backend Framework and APIs
- **FastAPI**: High-performance web framework for building APIs with Python
- **Flask**: Web framework for serving the annotation interface
- **Uvicorn**: ASGI server implementation for running FastAPI applications

### Machine Learning and AI
- **Google Gemini AI**: Large Language Model API for text generation and analysis
- **PyTorch**: Deep learning framework used for audio processing
- **TorchAudio**: Library for audio processing and feature extraction

### Audio Processing
- **SpeechRecognition**: Library for performing speech recognition
- **Pydub**: Audio processing library for handling various audio formats
- **Soundfile**: Library for reading and writing sound files

### Development and Utilities
- **Python 3.10**: Core programming language
- **Pydantic**: Data validation using Python type annotations
- **python-dotenv**: Environment variable management
- **python-multipart**: Library for handling multipart form data

### Project Structure
- RESTful API endpoints for audio processing and classification
- Web-based annotation interface
- Modular architecture with separate services and models
- Environment-based configuration management

## Technical Implementation

### Model Endpoints
The project exposes a RESTful API endpoint through FastAPI:

- `/process-audio` (POST)
  - Accepts: WAV audio files
  - Returns: JSON response containing:
    - Conversation transcript
    - Classification (Potential Customer or Unnecessary Call)
    - Category (if classified as Unnecessary)
    - Justification for the classification
    - Raw LLM output

### Voice Activity Detection (VAD)
The project utilizes Silero VAD (Voice Activity Detection) for precise speech detection:

- Implemented through PyTorch Hub
- Features:
  - Automatic resampling to 16kHz
  - Configurable speech detection threshold
  - Minimum speech duration settings
  - Stereo channel separation for customer/agent distinction
  - Intelligent speech segment detection

### Prompt Engineering with Gemini AI
The system employs sophisticated prompt engineering for call classification:

#### Classification Categories
- Guaranteed Product (warranty-related calls)
- Irrelevant Sector (non-business related)
- Installation (installation-only queries)
- Service Fee Rejected
- Customer Asked for Price
- Repeat Customer Call

#### LLM Configuration
- Model: `gemini-2.0-flash-001`
- Temperature: 0 (deterministic outputs)
- Top-p: 0.95 (focused responses)
- Custom safety settings
- Structured XML output format:
  ```xml
  <classification>[Result]</classification>
  <category>[Category if unnecessary]</category>
  <justification>[Detailed explanation]</justification>
  ```

### Processing Pipeline
1. Audio file upload handling
2. Stereo channel separation (customer/agent)
3. Speech detection using Silero VAD
4. Speech-to-text conversion
5. Conversation analysis via Gemini AI
6. Structured response generation

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
import os
import subprocess
import tempfile
import uuid
import torchaudio
import speech_recognition as sr
import torch
from fastapi import FastAPI, File, UploadFile, HTTPException
from pydantic import BaseModel
import re
from google import genai
from google.genai import types
from dotenv import load_dotenv


app = FastAPI()
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Load Silero VAD model and utilities from Torch Hub
model, utils = torch.hub.load(
    repo_or_dir="snakers4/silero-vad", model="silero_vad", force_reload=False)
(get_speech_ts, save_audio, read_audio, VADIterator, collect_chunks) = utils


def get_silero_speech_segments(audio_path: str,
                               target_sr: int = 16000,
                               threshold: float = 0.3,
                               min_speech_duration_ms: int = 400):
    """
    Loads a mono audio file, resamples it to target_sr if needed, and uses Silero VAD
    to obtain speech segments.
    """
    audio_tensor, sr = torchaudio.load(audio_path)
    if audio_tensor.shape[0] > 1:
        audio_tensor = audio_tensor[0].unsqueeze(0)
    if sr != target_sr:
        resampler = torchaudio.transforms.Resample(orig_freq=sr, new_freq=target_sr)
        audio_tensor = resampler(audio_tensor)
        sr = target_sr
    speech_timestamps = get_speech_ts(audio_tensor, model, sampling_rate=sr,
                                      threshold=threshold,
                                      min_speech_duration_ms=min_speech_duration_ms)
    return speech_timestamps, audio_tensor, sr

def get_transcription(audio_path, language="tr"):
    """
    Transcribe an audio file using Google Speech Recognition.
    """
    r = sr.Recognizer()
    with sr.AudioFile(audio_path) as source:
        audio = r.record(source)
    try:
        transcription = r.recognize_google(audio, language=language)
    except sr.UnknownValueError:
        transcription = "[Unrecognized]"
    except sr.RequestError as e:
        transcription = f"[Request error: {e}]"
    return transcription

def split_and_transcribe(audio_tensor, sr, segments, channel_label, chunks_dir):
    """
    Process each speech segment and return transcripts.
    """
    extra_samples = int(0.4 * sr)
    transcripts = []
    for i, seg in enumerate(segments):
        start = int(seg["start"])
        end = int(seg["end"])
        new_start = max(0, start - extra_samples)
        new_end = min(audio_tensor.shape[1], end + extra_samples)
        segment_audio = audio_tensor[:, new_start:new_end]
        
        raw_file_path = os.path.join(chunks_dir, f"{channel_label}_segment_{i}_raw.wav")
        torchaudio.save(raw_file_path, segment_audio, sample_rate=sr)
        
        converted_file_path = os.path.join(chunks_dir, f"{channel_label}_segment_{i}.wav")
        subprocess.run([
            "ffmpeg", "-y",
            "-i", raw_file_path,
            "-ar", "16000",
            "-ac", "1",
            converted_file_path
        ], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        
        transcription = get_transcription(converted_file_path)
        
        transcripts.append({
            "channel": channel_label,
            "start": new_start,
            "end": new_end,
            "transcription": transcription,
            "file": converted_file_path
        })
    return transcripts

def split_stereo_channels(input_path: str):
    """
    Splits a stereo WAV file into two mono files.
    """
    base, ext = os.path.splitext(input_path)
    left_path = f"{base}_customer_service{ext}"
    right_path = f"{base}_customer{ext}"
    
    subprocess.run([
        "ffmpeg", "-y",
        "-i", input_path,
        "-af", "pan=mono|c0=FL",
        left_path
    ], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    
    subprocess.run([
        "ffmpeg", "-y",
        "-i", input_path,
        "-af", "pan=mono|c0=FR",
        right_path
    ], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    
    return left_path, right_path

def align_dialogue(transcripts_left, transcripts_right):
    """
    Merge transcripts from both channels and sort them by start sample index.
    """
    all_transcripts = transcripts_left + transcripts_right
    all_transcripts.sort(key=lambda x: x["start"])
    return all_transcripts

def classify_transcript_with_llm(transcript_text: str) -> dict:
    """
    Process transcript with Gemini LLM and return classification.
    """
    client = genai.Client(api_key=GEMINI_API_KEY)

    system_prompt = """You are an AI assistant tasked with analyzing customer service call transcripts. Your goal is to determine whether each call represents a potential customer or an unnecessary call, and if unnecessary, to classify it into one of several predefined categories.
Here is the transcript of a customer service call in format:
<transcript>
{{TRANSCRIPT}}
<transcript>
Analyze the conversation in the transcript and determine if it represents a potential customer or an unnecessary call. If it's an unnecessary call, classify it into one of the following categories:
1. Guaranteed Product: The customer is calling about a product that is still under warranty.
2. Irrelevant Sector: The call is not related to the company's business sector.
3. Installation: The call is solely about product installation.
4. Service Fee Rejected: The customer rejects the service fee without considering the service.
5. Customer Asked for Price: The call is only to inquire about pricing without intent to purchase.
6. Repeat Customer Call: The customer is calling again about the same issue without new information.
Present your analysis in the following format:
<analysis>
<classification>[Potential Customer or Unnecessary Call]</classification>
<category>[If Unnecessary Call, specify the category]</category>
<justification>
[Provide a brief explanation for your classification, referencing specific parts of the conversation that support your decision.]
</justification>
</analysis>"""

    final_prompt = system_prompt.replace("{{TRANSCRIPT}}", transcript_text)

    generate_content_config = types.GenerateContentConfig(
        temperature=0,
        top_p=0.95,
        max_output_tokens=1024,
        safety_settings=[
            types.SafetySetting(category="HARM_CATEGORY_HATE_SPEECH", threshold="OFF"),
            types.SafetySetting(category="HARM_CATEGORY_DANGEROUS_CONTENT", threshold="OFF"),
            types.SafetySetting(category="HARM_CATEGORY_SEXUALLY_EXPLICIT", threshold="OFF"),
            types.SafetySetting(category="HARM_CATEGORY_HARASSMENT", threshold="OFF"),
        ],
        system_instruction=[types.Part.from_text(text=final_prompt)],
    )

    response = client.models.generate_content(
        model="gemini-2.0-flash-001",
        contents=[types.Content(role="user", parts=[types.Part.from_text(text=transcript_text)])],
        config=generate_content_config,
    )

    llm_text = response.text or ""

    classification_match = re.search(r"<classification>(.*?)</classification>", llm_text, re.DOTALL)
    category_match = re.search(r"<category>(.*?)</category>", llm_text, re.DOTALL)
    justification_match = re.search(r"<justification>(.*?)</justification>", llm_text, re.DOTALL)

    return {
        "llm_raw_output": llm_text,
        "classification": classification_match.group(1).strip() if classification_match else "",
        "category": category_match.group(1).strip() if category_match else "",
        "justification": justification_match.group(1).strip() if justification_match else ""
    }

class LLMResult(BaseModel):
    transcript: str
    classification: str
    category: str
    justification: str
    llm_raw_output: str

@app.post("/process-audio", response_model=LLMResult)
async def process_audio(file: UploadFile = File(...)):
    if not file.filename.endswith(".wav"):
        raise HTTPException(status_code=400, detail="Only .wav files are accepted.")
    
    with tempfile.TemporaryDirectory() as tmpdir:
        # Save uploaded file
        input_path = os.path.join(tmpdir, f"{uuid.uuid4()}_input.wav")
        with open(input_path, "wb") as f:
            f.write(await file.read())
        
        # Split channels
        left_audio_path, right_audio_path = split_stereo_channels(input_path)
        
        # Get segments and transcribe
        left_segments, left_audio, left_sr = get_silero_speech_segments(left_audio_path)
        right_segments, right_audio, right_sr = get_silero_speech_segments(right_audio_path)
        
        # Filter customer segments if needed
        if left_segments:
            first_service_start = left_segments[0]['start'] - 2 * left_sr
            right_segments = [seg for seg in right_segments if seg['start'] >= first_service_start]
        
        # Create chunks directory
        chunks_dir = os.path.join(tmpdir, "audio_chunks")
        os.makedirs(chunks_dir, exist_ok=True)
        
        # Process and transcribe segments
        transcripts_left = split_and_transcribe(left_audio, left_sr, left_segments, "customer_service", chunks_dir)
        transcripts_right = split_and_transcribe(right_audio, right_sr, right_segments, "customer", chunks_dir)
        
        # Align dialogue and create transcript
        dialogue = align_dialogue(transcripts_left, transcripts_right)
        transcript_text = "\n".join([f"{entry['channel']}: {entry['transcription']}" for entry in dialogue])
        
        # Get LLM classification
        llm_result = classify_transcript_with_llm(transcript_text)
        
        return LLMResult(
            transcript=transcript_text,
            classification=llm_result["classification"],
            category=llm_result["category"],
            justification=llm_result["justification"],
            llm_raw_output=llm_result["llm_raw_output"]
        )
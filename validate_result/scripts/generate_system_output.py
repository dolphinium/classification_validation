import os
import csv
import requests

# Your FastAPI endpoint
API_ENDPOINT = "http://127.0.0.1:8000/process-audio"

# Folder containing .wav test files
TEST_WAVS_FOLDER = "../data/audio_files/"

# CSV file to store system outputs
OUTPUT_CSV = "../data/system_output.csv"

def main():
    # Gather .wav files
    wav_files = [f for f in os.listdir(TEST_WAVS_FOLDER) if f.endswith(".wav")]
    wav_files.sort()

    # Ensure output directory exists
    os.makedirs(os.path.dirname(OUTPUT_CSV), exist_ok=True)
    
    # Define the CSV fieldnames
    fieldnames = ["file_id", "transcript", "classification", "category", "justification"]

    # Open the CSV file once at the start and write the header
    with open(OUTPUT_CSV, mode="w", newline="", encoding="utf-8") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()  # Write the CSV header only once at the beginning

        for wav_file in wav_files:
            file_path = os.path.join(TEST_WAVS_FOLDER, wav_file)
            file_id = wav_file.split(".")[0]
            print(f"Processing {wav_file}...")

            # Send the file to the model endpoint
            with open(file_path, "rb") as f:
                response = requests.post(API_ENDPOINT, files={"file": (wav_file, f, "audio/wav")})

            if response.status_code == 200:
                res_json = response.json()
                # Expecting keys: transcript, classification, category, justification
                row_data = {
                    "file_id": file_id,
                    "transcript": res_json.get("transcript", ""),
                    "classification": res_json.get("classification", ""),
                    "category": res_json.get("category", ""),
                    "justification": res_json.get("justification", "")
                }
                # Write a single row per successful response
                writer.writerow(row_data)
                
                # Flush to ensure data is physically written to disk after each processed file
                csvfile.flush()
            else:
                print(f"Error for file {wav_file} -> HTTP {response.status_code}: {response.text}")

    print(f"\nFinished writing system outputs to {OUTPUT_CSV}")


if __name__ == "__main__":
    main()

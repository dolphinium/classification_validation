suggested env: conda
git clone "url"
cd "dir"

crate conda environment and install the requirements:
conda create -n tts_annotate python=3.10
conda activate tts_annotate
pip install -r requirements.txt


for venv
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt


cd validate_result


get the gemini api key from this [address](https://aistudio.google.com/app/u/0/apikey): and set the environment variable into .ENV file
GEMINI_API_KEY=YOUR_GEMINI_API_KEY


place the audio files that I sent you under the data/audio_files folder

start the uvicorn server for backend api
uvicorn pipeline_api:app --reload


start the flask app
python app.py


to generate llm responses:
cd scripts
python generate_system_output.py

start annotate

after finishing annotate upload the annotated.csv to this drive:
DRIVE LINK
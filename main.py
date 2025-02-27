from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from google.cloud import speech
import io

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 1. Функция для анализа текста
def analyze_transcript(transcript: str):
    words = transcript.split()
    word_count = len(words)
    unique_words = len(set(words))
    
    lexical_diversity = 0
    if word_count > 0:
        lexical_diversity = unique_words / word_count

    score = 5.0
    if word_count > 50:
        score += 1.0
    if lexical_diversity > 0.5:
        score += 1.0
    if score > 9:
        score = 9.0

    return {
        "ielts_score_approx": round(score, 1),
        "word_count": word_count,
        "unique_words": unique_words
    }

# 2. Ваш эндпоинт для загрузки и распознавания аудио
@app.post("/upload-audio")
async def upload_audio(file: UploadFile = File(...)):
    content = await file.read()

    client = speech.SpeechClient.from_service_account_json("service-account-key.json")
    audio = speech.RecognitionAudio(content=content)
    config = speech.RecognitionConfig(
        encoding=speech.RecognitionConfig.AudioEncoding.ENCODING_UNSPECIFIED,
        language_code="en-US",
    )
    response = client.recognize(config=config, audio=audio)

    transcript = ""
    for result in response.results:
        transcript += result.alternatives[0].transcript

    # 3. Вызываем функцию и возвращаем результат
    analysis = analyze_transcript(transcript)
    return {"transcript": transcript, "analysis": analysis}

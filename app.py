import streamlit as st
import google.generativeai as genai
from murf import Murf
from deep_translator import GoogleTranslator
import requests
import base64
import re
import time
import subprocess
import tempfile
import os

# -----------------------------------------
# API CONFIG
# -----------------------------------------

genai.configure(api_key="AIzaSyD5dqXE-rMqWA9OeC4k4pH0fAfg1gPzTes")
murf_client = Murf(api_key="ap2_353f83f1-51b5-421e-b57d-5a817941e293")

# -----------------------------------------
# LANGUAGE MAPS
# -----------------------------------------

voice_map = {
    "English": "en-IN-eashwar",
    "Tamil": "ta-IN-iniya",
    "Hindi": "hi-IN-priya",
    "Bengali": "bn-IN-anika",
    "Spanish": "es-ES-javier",
    "French": "fr-FR-thomas",
    "German": "de-DE-lukas",
    "Italian": "it-IT-luca",
    "Dutch": "nl-NL-max",
    "Portuguese": "pt-BR-gabriel",
    "Chinese": "zh-CN-xiaoyan",
    "Japanese": "ja-JP-haruka",
    "Korean": "ko-KR-minseo"
}

lang_code_map = {
    "Tamil": "ta", "Hindi": "hi", "Bengali": "bn",
    "Spanish": "es", "French": "fr", "German": "de",
    "Italian": "it", "Dutch": "nl", "Portuguese": "pt",
    "Chinese": "zh-CN", "Japanese": "ja", "Korean": "ko"
}

word_limit_map = {
    "1": 50,
    "2": 100,
    "3": 150,
    "5": 400,
    "8": 2500
}

# -----------------------------------------
# STREAMLIT UI
# -----------------------------------------

st.set_page_config(page_title="Juggie Learn", layout="wide")
st.title("📚 Juggie.Learn — AI Study Buddy")

left, right = st.columns(2)

with left:
    question = st.text_area("Enter your question")
    subject = st.text_input("Subject (e.g., Science)")
    marks = st.selectbox("Select Marks", ["1", "2", "3", "5", "8"])

with right:
    language = st.selectbox(
        "Choose your output language",
        ["English", "Tamil", "Hindi", "Bengali", "Spanish",
         "French", "German", "Italian", "Dutch", "Portuguese",
         "Chinese", "Japanese", "Korean"]
    )

submit = st.button("✨ Generate Answer")

# -----------------------------------------
# GEMINI
# -----------------------------------------

def ask_gemini(prompt):
    try:
        model = genai.GenerativeModel("gemini-2.0-flash")
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"[ERROR] {e}"

# -----------------------------------------
# TEXT CLEANING
# -----------------------------------------

def clean_text(text):
    text = text.replace("\n", " ")
    text = re.sub(r"\s+", " ", text)
    return text.strip()

def split_into_sentences(text):
    return re.split(r'(?<=[.!?]) +', text)

def build_safe_chunks(text, limit=2500):
    sentences = split_into_sentences(text)
    chunks = []
    current = ""

    for sentence in sentences:
        if len(current) + len(sentence) + 1 <= limit:
            current += sentence + " "
        else:
            chunks.append(current.strip())
            current = sentence + " "

    if current:
        chunks.append(current.strip())

    return chunks

# -----------------------------------------
# MURF TTS (Single Chunk)
# -----------------------------------------

def murf_tts_chunk(text, voice_id):
    text = clean_text(text)
    for attempt in range(3):
        try:
            res = murf_client.text_to_speech.generate(
                text=text,
                voice_id=voice_id,
                format="MP3"
            )
            url = res.audio_file
            audio = requests.get(url, timeout=25).content
            return audio
        except Exception:
            time.sleep(1)
    return None

# -----------------------------------------
# AUDIO MERGE USING FFMPEG (NO PYDUB)
# -----------------------------------------

def merge_audio_files(audio_bytes_list):
    with tempfile.TemporaryDirectory() as tmpdir:
        input_files = []

        # Save each chunk to temporary MP3 files
        for i, audio_bytes in enumerate(audio_bytes_list):
            path = os.path.join(tmpdir, f"part{i}.mp3")
            with open(path, "wb") as f:
                f.write(audio_bytes)
            input_files.append(path)

        # File list for ffmpeg
        list_path = os.path.join(tmpdir, "list.txt")
        with open(list_path, "w") as f:
            for fpath in input_files:
                f.write(f"file '{fpath}'\n")

        merged_output = os.path.join(tmpdir, "merged.mp3")

        subprocess.run(
            ["ffmpeg", "-y", "-f", "concat", "-safe", "0",
             "-i", list_path, "-acodec", "copy", merged_output],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )

        with open(merged_output, "rb") as f:
            return f.read()

# -----------------------------------------
# make_full_voice (uses Murf + ffmpeg)
# -----------------------------------------

def make_full_voice(text, voice_id):
    chunks = build_safe_chunks(text)
    audio_parts = []

    for i, chunk in enumerate(chunks):
        st.write(f"🔉 Generating voice part {i+1}/{len(chunks)}...")
        audio = murf_tts_chunk(chunk, voice_id)
        if audio:
            audio_parts.append(audio)
        else:
            st.error(f"❌ Failed to generate part {i+1}")

    if not audio_parts:
        return None

    return merge_audio_files(audio_parts)

# -----------------------------------------
# TRANSLATION
# -----------------------------------------

def translate(text, lang):
    try:
        if lang not in lang_code_map:
            return text
        return GoogleTranslator(source="auto", target=lang_code_map[lang]).translate(text)
    except:
        return text

# -----------------------------------------
# MAIN LOGIC
# -----------------------------------------

if submit:
    if not question:
        st.warning("Please enter a question.")
        st.stop()

    max_words = word_limit_map[marks]

    prompt = f"""
You are Juggie — a friendly student who explains concepts casually like helping a best friend before an exam.

Subject: {subject}
Marks: {marks}
Language: {language}
Question: {question}

Write an answer for {marks} marks ONLY in {language}.

STYLE RULES:
- Casual, friendly, student-like tone
- Simple everyday language
- No textbook tone
- Small funny or relatable examples
- Avoid brackets
- Max {max_words} words
- Use only {language} script except basic English tech words

Begin answer directly. No headings.
"""

    with st.spinner("Thinking…"):
        raw_answer = ask_gemini(prompt)

    if raw_answer.startswith("[ERROR]"):
        st.error(raw_answer)
        st.stop()

    final_answer = translate(raw_answer, language)

    # Trim to word limit
    words = final_answer.split()
    final_answer = " ".join(words[:max_words])

    st.subheader(f"📘 Juggie Says ({language})")
    st.write(final_answer)

    st.divider()

    voice_id = voice_map.get(language, "en-IN-eashwar")

    with st.spinner("Generating full audio…"):
        full_audio = make_full_voice(final_answer, voice_id)

    if full_audio:
        st.success("🎧 Full audio is ready!")
        st.audio(full_audio, format="audio/mp3")

        b64 = base64.b64encode(full_audio).decode()
        st.markdown(
            f'<a href="data:audio/mp3;base64,{b64}" download="Juggie_full_audio.mp3">Download Full Audio</a>',
            unsafe_allow_html=True
        )

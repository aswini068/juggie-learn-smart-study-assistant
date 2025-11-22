import streamlit as st
import google.generativeai as genai
from murf import Murf
from deep_translator import GoogleTranslator
import requests
import base64
import re
import time
import sys
import types

# --- PATCH FOR STREAMLIT CLOUD: Prevent pyaudioop import ---
dummy = types.ModuleType("pyaudioop")
sys.modules["pyaudioop"] = dummy
# -----------------------------------------------------------

from pydub import AudioSegment
AudioSegment.converter = "/usr/bin/ffmpeg"
AudioSegment.ffmpeg = "/usr/bin/ffmpeg"
AudioSegment.ffprobe = "/usr/bin/ffprobe"
from io import BytesIO

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
# TEXT CLEANING FOR MURF
# -----------------------------------------

def clean_text(text):
    text = text.replace("\n", " ")
    text = re.sub(r"\s+", " ", text)
    return text.strip()

# SPLIT BY SENTENCES
def split_into_sentences(text):
    return re.split(r'(?<=[.!?]) +', text)

# BUILD SAFE CHUNKS (<2500 chars)
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
# MURF TTS - FOR EACH CHUNK
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
# FULL AUDIO - MERGED (Option B)
# -----------------------------------------

def make_full_voice(text, voice_id):
    text = clean_text(text)
    chunks = build_safe_chunks(text)

    final_audio = AudioSegment.empty()

    for i, chunk in enumerate(chunks):
        st.write(f"🔉 Generating voice part {i+1}/{len(chunks)}...")

        audio_bytes = murf_tts_chunk(chunk, voice_id)
        if not audio_bytes:
            st.error(f"❌ Failed to generate part {i+1}")
            continue

        part_audio = AudioSegment.from_file(BytesIO(audio_bytes), format="mp3")
        final_audio += part_audio

    buf = BytesIO()
    final_audio.export(buf, format="mp3")
    return buf.getvalue()

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
You are Juggie — a super friendly student who explains things casually like a best friend during last-minute exam revision.

Subject: {subject}
Marks: {marks}
Language: {language}
Question: {question}

Now write a {marks}-mark answer ONLY in {language}.

STYLE RULES:
- Sound like a friendly student, not a teacher.
- Very simple, casual, everyday language.
- No textbook tone.
- Use funny or relatable examples students use while studying.
- No formal definitions unless needed.
- No long complex sentences.
- Explain like you're helping a friend just before the exam.
- Add small real-life comparisons.
- Avoid brackets.
- DO NOT exceed {max_words} words.
- Use ONLY {language} script (except common English tech words like “data”, “mobile”, “network”, etc.).

Start the answer directly. No headings, no introduction.
"""

    with st.spinner("Thinking…"):
        raw_answer = ask_gemini(prompt)

    if raw_answer.startswith("[ERROR]"):
        st.error(raw_answer)
        st.stop()

    final_answer = translate(raw_answer, language)

    # Cut to max words
    words = final_answer.split()
    final_answer = " ".join(words[:max_words])

    st.subheader(f"📘 Juggie Says ({language})")
    st.write(final_answer)

    st.divider()

    # AUDIO
    voice_id = voice_map.get(language, "en-IN-eashwar")

    with st.spinner("Generating full audio…"):
        merged_audio = make_full_voice(final_answer, voice_id)

    if merged_audio:
        st.success("🎧 Full audio is ready!")
        st.audio(merged_audio, format="audio/mp3")

        b64 = base64.b64encode(merged_audio).decode()
        st.markdown(
            f'<a href="data:audio/mp3;base64,{b64}" download="Juggie_full_audio.mp3">🎧 Download Full Audio</a>',
            unsafe_allow_html=True
        )

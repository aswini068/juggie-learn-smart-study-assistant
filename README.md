# juggie-learn-smart-study-assistant

Below is a **clean, professional, complete README.md** tailored **specifically for your project: Juggie Learn — Smart Study Assistant**.

You can paste this directly into your GitHub repository.

---

# 📘 **Juggie Learn — Smart Study Assistant**

*A multilingual AI-powered study buddy that explains concepts like a best friend and generates natural voice narration for students.*

---

## 📝 **About the Project**

**Juggie Learn** is an AI-driven educational assistant designed to help students understand study concepts in a simple, friendly, and relatable way.
The system uses **Gemini Flash 2.0** for generating answers and **Murf AI TTS** for producing clear voice narration in multiple Indian and international languages.

The goal of the project is to create a **fun, student-friendly AI** that:

* Explains answers casually (not like a textbook)
* Supports Indian language scripts
* Generates audio responses for quick listening
* Works with mark-based answer length
* Helps with last-minute exam preparation

---

## ⭐ **Features**

### 🔹 **AI-Powered Q&A Generation**

* Uses *Google Gemini Flash 2.0* to generate smart and simplified answers.
* Automatically adjusts answer length based on selected **marks (1, 2, 3, 5, or 8)**.

### 🔹 **Multilingual Output**

Supports multiple Indian and international languages:

* Tamil
* Hindi
* Bengali
* English
* Kannada
* Japanese
* Korean
* and more…

### 🔹 **Friendly Conversational Style**

* Answers are generated in a **friendly, student-style tone**.
* No textbook jargon.
* Uses relatable examples.

### 🔹 **High-Quality Voice Output**

* Uses **Murf AI TTS** to convert answers into natural-sounding speech.
* Automatically splits long answers and merges audio safely.
* Provides a **downloadable MP3** file.

### 🔹 **Lightweight & Cloud Deployable**

* Fully deployable on **Streamlit Cloud**
* No heavy ML libraries required
* Works smoothly on free hosting

---

## 🧰 **Requirements**

### **Backend / Runtime**

* Python **3.10** (recommended for Streamlit Cloud)
* Streamlit for UI rendering
* Gemini API key (stored securely in Streamlit Secrets)
* Murf API key (also stored securely)

### **Python Dependencies**

* `streamlit`
* `google-generativeai`
* `murf`
* `deep-translator`
* `requests`
* `base64`

### **Development Environment**

* **VS Code** or **PyCharm**
* **Git + GitHub** for version control
* Basic internet connectivity for API access

---

## 🏗 **System Architecture**

```
User Input → Gemini Prompt → AI Answer → Language Translation → Murf TTS → Audio Merge → Final Output (Text + MP3)
```

### Flow Breakdown:

1. Student enters topic, question, language, and marks.
2. Gemini Flash generates the answer based on marks.
3. Deep Translator converts answer into chosen language.
4. Murf TTS converts text into natural voice chunks.
5. MP3 chunks are merged without ffmpeg (safe concatenation).
6. Output displayed with downloadable audio.

---

## 📤 **Sample Outputs**

### **Output 1 – AI Written Answer**

* Clean paragraph
* Student-friendly explanation
* Uses selected language script

### **Output 2 – Voice Output**

* Smooth, natural voice
* Multi-part answers merged automatically
* Downloadable MP3 file (Juggie_full_audio.mp3)

---

## 🎯 **Impact**

Juggie Learn helps students by:

* Making study answers easy to understand
* Reducing exam stress
* Supporting Indian regional languages
* Making studying accessible with voice content
* Providing quick revision with conversational explanations

This project encourages accessible education, especially for rural or regional-language students.

---

## 📚 **References**

* Google AI Studio – Gemini Models
* Murf AI Documentation
* Streamlit Official Documentation

---

## 🛠 **How to Run Locally**

1. Clone the repository:

```
git clone https://github.com/aswini068/juggie-learn-smart-study-assistant.git
cd juggie-learn-smart-study-assistant
```

2. Install dependencies:

```
pip install -r requirements.txt
```

3. Add your API keys in `.streamlit/secrets.toml`:

```
GEMINI_API_KEY = "YOUR_KEY"
MURF_API_KEY = "YOUR_KEY"
```

4. Run the project:

```
streamlit run app.py
```

---

## 🚀 **Deployment (Streamlit Cloud)**

1. Push your code to GitHub.
2. Go to [https://share.streamlit.io](https://share.streamlit.io)
3. Select your repository.
4. Add `GEMINI_API_KEY` and `MURF_API_KEY` under “Secrets”.
5. Deploy with Python version set to **3.10**.

---


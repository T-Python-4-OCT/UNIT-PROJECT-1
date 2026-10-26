# 🕌 Taysir — تيسير

### 📖 Your Intelligent Quran Companion

Taysir is an Arabic Quran application built with Python, combining Quran reading, navigation, search, Tafsir Al-Muyassar, audio recitation, and AI-powered interaction through Arabic commands.

---

## ✨ Features

- 📖 Read Quranic verses in Arabic.
- 🧭 Navigate between surahs and ayahs.
- 🎯 Jump directly to a specific ayah.
- 🔎 Search Quranic text.
- 📚 Access Tafsir Al-Muyassar.
- 🎧 Listen to Quran recitation.
- 🔁 Repeat verses and play complete surahs.
- ⏹️ Stop audio playback.
- 🤖 Interact with the Smart Agent using Arabic commands.
- 🎙️ Use voice-related features where supported.
- 🖥️ Navigate through an interactive CLI built with Rich.

---

## 🤖 AI Agents

### 🧠 1. Taysir AI Agent

The `TaysirAIAgent` component provides AI-assisted interaction with the application.

- 🏠 Runs language-model inference locally through Ollama.
- 🧩 Uses **Qwen3:14B** as the configured language model.
- 🔗 Connects to Ollama through its local HTTP endpoint.
- 🗂️ Uses structured responses to support intent interpretation and command handling.
- 📖 Connects natural-language requests with available Quran features.

**Model configuration**

| Component | Technology |
|---|---|
| 🧠 Language model | Qwen3:14B |
| ⚙️ Runtime | Ollama |
| 🌐 Local endpoint | `http://127.0.0.1:11434` |

### 💬 2. Smart Agent & Intent Parser

The Smart Agent connects Arabic commands with supported application actions.

- 🗣️ Understands supported Arabic command patterns.
- 📖 Handles Quran reading and navigation requests.
- 📚 Routes tafsir requests to the relevant functions.
- 🔎 Supports Quran-related search commands.
- 🔀 Works alongside the direct CLI menu.

The `IntentParser` interprets supported command patterns, while `command_handler.py` coordinates their execution.

### 🎙️ 3. Voice Agent

The voice components provide voice interaction where dependencies and local configuration are available.

- 🎤 Supports voice-related interaction.
- 🔗 Integrates with the application's command workflow.
- 💬 Complements typed Arabic commands.

Voice functionality depends on the installed packages and local environment.

---

## 🛠️ Technology Stack

- �� Python
- 🧠 Qwen3:14B
- ⚙️ Ollama
- 🖥️ Rich
- �� `arabic-reshaper`
- ↔️ `python-bidi`
- 🔊 Audio playback components
- 📄 JSON-based Quran and tafsir data

---

## 📋 Requirements

- 🐍 Python 3.10 or newer
- 📦 pip
- 🧠 Ollama for local AI inference
- 📚 Quran and tafsir data files
- 🎙️ Additional voice dependencies when voice features are enabled

---

## 🚀 Installation

### 1️⃣ Clone the repository

```bash
git clone https://github.com/iimustafa/UNIT-PROJECT-1.git
cd UNIT-PROJECT-1
```

### 2️⃣ Create a virtual environment

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3️⃣ Install dependencies

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### 4️⃣ Prepare the local AI model

Install Ollama, then download the configured model:

```bash
ollama pull qwen3:14b
```

If Ollama is not already running as a service, start it with:

```bash
ollama serve
```

---

## ▶️ Run Taysir

Start the application:

```bash
python main.py
```

Use the Arabic CLI menu to read the Quran, navigate verses, search, access tafsir, control recitation, and interact with the Smart Agent.

---

## 📁 Project Structure

```text
Taysir/
├── commands/       # 🧭 CLI commands and intent parsing
├── data/           # 📚 Quran and tafsir data
├── interface/      # 🖥️ Arabic CLI interface
├── player/         # 🎧 Quran audio playback
├── quran/          # 📖 Quran reading and navigation
├── tafsir/         # 📚 Tafsir access
├── voice/          # 🎙️ Voice components
├── ai_agent.py     # 🤖 AI agent
├── main.py         # 🚀 Application entry point
├── requirements.txt
└── README.md
```

---

## 📝 Development Notes

- 🔧 Taysir is an ongoing project.
- 🌐 Arabic right-to-left rendering can vary between terminal emulators.
- 📜 Preserve the attribution and licensing information for Quranic text, tafsir, and third-party components.
- 🛡️ Use reliable sources for Quranic text and tafsir.

---

## 📄 License

Add the appropriate project license and retain the licenses of third-party code and data sources.

---

### 🌙 Built with care to make Quran reading and reflection easier.

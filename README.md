# 🤖 Amulya AI — Conversational Voice Assistant

> An intelligent, conversational voice assistant built in Python, inspired by Google Gemini. Introduces itself and engages in natural dialogue.

---

## Features

- **Instant Greeting** — Introduces itself immediately when you start the app
- **Conversational AI** — Engages in natural dialogue like Google Gemini (no wake word needed)
- **Voice Recognition** — Understands natural speech via Google Speech Recognition
- **Neural Voice Synthesis** — Responds with high-quality neural voice using Edge TTS
- **General Q&A** — Answers any question using Pollinations.ai API (no API key needed)
- **Conversation Memory** — Remembers context within a session and persists to disk
- **Smart Commands** — Voice control for common tasks:
  - 🌐 Web browsing (YouTube, Google, GitHub, LinkedIn, Reddit, etc.)
  - 🎵 Music playback via YouTube
  - ⏰ Time, date, weather (wttr.in)
  - 📸 Screenshots
  - 😄 Programming jokes
  - 📁 File operations and system control
- **Intelligent Interruption** — Say "Hey Amulya" anytime to interrupt responses
- **Persistent Logging** — All interactions logged to `logs/` directory
- **Offline Fallback** — Graceful error handling when internet is unavailable

---

## Quick Start

### Prerequisites
- Python 3.11+
- A working microphone and speakers

### Installation

```bash
# Clone or download the project
cd amulya-ai-assistant

# Create virtual environment
python -m venv .venv_new
.venv_new\Scripts\activate          # Windows
source .venv_new/bin/activate       # macOS/Linux

# Install dependencies
pip install -r requirements.txt
```

### Run the Assistant

**Easiest way - Double-click:**
```
launch.vbs
```

**Or from terminal:**
```bash
python main.py
```

**Or with launch script:**
```powershell
.\run.ps1
.\run.ps1 -Logs        # Show recent logs
```

---

## How It Works

When you start Amulya AI:

1. **🎤 Introduction** — Amulya introduces itself and asks what you need
2. **👂 Listening** — You ask a question (e.g., "Who is Narendra Modi?")
3. **🧠 Processing** — AI thinks about the answer
4. **🔊 Speaking** — Amulya responds conversationally and naturally
5. **🔁 Continuous** — Asks if you have more questions and keeps listening

---

## Voice Commands

Ask anything! Here are examples:

### General Questions
- "Who is Narendra Modi?"
- "What is artificial intelligence?"
- "Tell me about Python programming"
- "How do solar panels work?"

### Web & Media
- "Open YouTube"
- "Open Google"
- "Play Bohemian Rhapsody"
- "Search Wikipedia for Isaac Newton"

### Utilities
- "What time is it?"
- "What's the weather in New York?"
- "Take a screenshot"
- "Tell me a joke"

### System Control
- "Volume up"
- "Mute"
- "Close window"
- "Type hello world"

### Memory
- "Clear memory" or "Forget everything" — Reset conversation
- "Exit" or "Quit" — Stop the assistant

---

## Project Structure

```
amulya-ai/
├── main.py                    # Entry point
├── amulya_ai.py              # Main dialogue loop
├── ai_brain.py               # AI conversation engine
├── commands.py               # Voice command handlers
├── speech_engine.py          # Text-to-speech
├── voice_input.py            # Speech recognition
├── interrupt_core.py         # Interrupt handling
├── logger.py                 # Logging system
├── persistent_memory.py      # Conversation history
├── config.py                 # Configuration
├── ui.py                     # Terminal UI
├── musicLibrary.py           # Music shortcuts
├── run.bat                   # Launch script (batch)
├── run.ps1                   # Launch script (PowerShell)
├── launch.vbs                # Quick launch (double-click)
├── logs/                     # Activity logs
├── assets/                   # Screenshots & media
└── requirements.txt          # Dependencies
```

---

## Configuration

Edit `config.py` to customize:

- **WAKE_TRIGGERS** — Phrases to interrupt responses
- **ENERGY_THRESHOLD** — Microphone sensitivity
- **MAX_MEMORY** — Conversation history length
- **PERSIST_MEMORY** — Save conversation to disk
- **TTS_VOICE** — Voice type / language
- **WEBSITES** — Quick-launch URLs

---

## API & Libraries

- **Speech Recognition** — Google Speech Recognition API
- **Text-to-Speech** — Edge TTS (Microsoft neural voices)
- **AI Engine** — Pollinations.ai (free, no key required)
- **Audio** — Pygame
- **CLI** — Rich (beautiful terminal output)

---

## Logs

View activity logs:
```powershell
Get-ChildItem logs/
Get-Content logs/amulya_ai_*.log
```

Or use the launch script:
```powershell
.\run.ps1 -Logs
```

---

## Tips

- Speak clearly and naturally - no need to be formal
- Amulya maintains conversation context, so follow-up questions work great
- If noisy, adjust `ENERGY_THRESHOLD` in `config.py` (lower = more sensitive)
- Say "Hey Amulya" anytime to interrupt a response
- Check `logs/` folder for debugging

---

## Troubleshooting

**No microphone detected?**
- Check if your mic is plugged in and enabled
- Try adjusting ENERGY_THRESHOLD in config.py

**AI not responding?**
- Check internet connection (uses Pollinations.ai API)
- Check logs in `logs/` folder for errors

**Speech not working?**
- Ensure speakers are unmuted
- Check TTS_VOICE setting in config.py

---

## Future Enhancements

- [ ] Local LLM support (offline mode)
- [ ] Custom wake word training
- [ ] Multi-language support
- [ ] GUI dashboard
- [ ] Integration with smart home devices

---

## License

MIT License - Feel free to modify and distribute!

---

**Made with ❤️ for conversational AI**
- **MAX_HISTORY** — Number of conversation turns to remember

---

## Tech Stack

- **Speech Recognition**: `SpeechRecognition` + Google API
- **Text-to-Speech**: `pyttsx3`
- **AI Engine**: Pollinations.ai (free, no key)
- **Wikipedia**: `wikipedia` library
- **Weather**: wttr.in (free)
- **Jokes**: `pyjokes`
- **Screenshots**: `pyautogui`

---

## License

MIT License — feel free to use, modify, and share.

---

> Built with ❤️ by Amulya

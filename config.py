# ============================================================
#  config.py  —  Amulya AI Configuration (Central Settings)
# ============================================================
import os
from dotenv import load_dotenv

load_dotenv()

ASSISTANT_NAME = "Amulya AI"

# ── Wake Word Triggers ──
# All lowercase variations that Google STT might hear when you say "Hey Amulya"
WAKE_TRIGGERS = frozenset([
    "amulya", "amulia", "amelia", "amalya", "amulaya",
    "a mulya", "a moolya", "moolya", "amul", "amilia",
    "hey amulya", "hey amelia", "hey amulia",
])

# ── Microphone ──
ENERGY_THRESHOLD = 300          # Mic sensitivity (lower = more sensitive)
WAKE_TIMEOUT     = 5            # Seconds to wait for wake word before retrying
WAKE_PHRASE      = 3            # Max seconds for wake word utterance
CMD_TIMEOUT      = 10           # Seconds to wait for a command
CMD_PHRASE       = 20           # Max seconds for a full command

# ── AI Engine ──
AI_URL     = os.getenv("AI_URL", "https://text.pollinations.ai/")
MAX_MEMORY = 20
PERSIST_MEMORY = True           # Save conversation history to disk

AI_PROMPT = (
    f"You are {ASSISTANT_NAME}, an intelligent and friendly voice assistant inspired by Google Gemini. "
    "Your answers are spoken aloud, so talk naturally and conversationally like a real person would. "
    "Be warm, engaging, and informative. Use natural language without formatting, bullets, or asterisks. "
    "No markdown. No emojis. Keep answers between 60-120 words - detailed enough to be helpful but concise enough to speak naturally. "
    "Sound like a knowledgeable friend having a real conversation, not reading from a textbook. "
    "If asked about people, places, or events, provide context and interesting details in a storytelling way."
)

# ── Edge TTS ──
TTS_VOICE = "en-US-ChristopherNeural"   # High-quality neural male voice

# ── Quick-launch websites ──
WEBSITES = {
    "youtube":   "https://youtube.com",
    "google":    "https://google.com",
    "github":    "https://github.com",
    "linkedin":  "https://linkedin.com",
    "instagram": "https://instagram.com",
    "facebook":  "https://facebook.com",
    "twitter":   "https://twitter.com",
    "chatgpt":   "https://chat.openai.com",
    "reddit":    "https://reddit.com",
}

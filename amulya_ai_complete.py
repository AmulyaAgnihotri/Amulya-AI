# ============================================================
#  amulya_ai_complete.py  —  Complete Amulya AI Voice Assistant
#  All-in-one consolidated file for easy integration
# ============================================================

import os
import sys
import logging
import threading
import time
import random
import asyncio
import json
import datetime
import subprocess
import webbrowser
import requests
from datetime import datetime as dt

# Third-party imports
import pygame
import edge_tts
import speech_recognition as sr
import pyjokes
import pyautogui
import keyboard
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich import box

# Configure stdout for UTF-8
sys.stdout.reconfigure(encoding="utf-8")

# ============================================================
#  CONFIGURATION SECTION
# ============================================================

ASSISTANT_NAME = "Amulya AI"

# Wake Word Triggers
WAKE_TRIGGERS = frozenset([
    "amulya", "amulia", "amelia", "amalya", "amulaya",
    "a mulya", "a moolya", "moolya", "amul", "amilia",
    "hey amulya", "hey amelia", "hey amulia",
])

# Microphone Settings
ENERGY_THRESHOLD = 300
WAKE_TIMEOUT = 5
WAKE_PHRASE = 3
CMD_TIMEOUT = 10
CMD_PHRASE = 20

# AI Engine Settings
AI_URL = "https://text.pollinations.ai/"
MAX_MEMORY = 20
PERSIST_MEMORY = True
TTS_VOICE = "en-US-ChristopherNeural"

# Websites
WEBSITES = {
    "youtube": "https://youtube.com",
    "google": "https://google.com",
    "github": "https://github.com",
    "linkedin": "https://linkedin.com",
    "instagram": "https://instagram.com",
    "facebook": "https://facebook.com",
    "twitter": "https://twitter.com",
    "chatgpt": "https://chat.openai.com",
    "reddit": "https://reddit.com",
}

# Music Library
MUSIC_LIBRARY = {
    "stealth": "https://www.youtube.com/watch?v=U47Tr9GQ_WE",
    "march": "https://www.youtube.com/watch?v=Xqeq4b5u_Xw",
    "skyfall": "https://www.youtube.com/watch?v=DeumyOzKqgI",
    "wolfs": "https://www.youtube.com/watch?v=ThCH0U6aJpU",
}

AI_PROMPT = (
    f"You are {ASSISTANT_NAME}, an intelligent and friendly voice assistant inspired by Google Gemini. "
    "Your answers are spoken aloud, so talk naturally and conversationally like a real person would. "
    "Be warm, engaging, and informative. Use natural language without formatting, bullets, or asterisks. "
    "No markdown. No emojis. Keep answers between 60-120 words - detailed enough to be helpful but concise enough to speak naturally. "
    "Sound like a knowledgeable friend having a real conversation, not reading from a textbook. "
    "If asked about people, places, or events, provide context and interesting details in a storytelling way."
)

# ============================================================
#  LOGGING SYSTEM
# ============================================================

os.makedirs("logs", exist_ok=True)
logger = logging.getLogger("Amulya_AI")
logger.setLevel(logging.DEBUG)

log_file = f"logs/amulya_ai_{dt.now().strftime('%Y%m%d_%H%M%S')}.log"
file_handler = logging.FileHandler(log_file, encoding='utf-8')
file_handler.setLevel(logging.DEBUG)

formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

# ============================================================
#  UI SYSTEM
# ============================================================

con = Console(highlight=False)

def ui_banner():
    con.print()
    con.print(f"  [bold cyan]━━━  {ASSISTANT_NAME}  ━━━[/bold cyan]")
    con.print(f"  [dim]Voice assistant  ·  System online[/dim]")
    con.print()

def ui_status(msg, style="dim"):
    con.print(f"  [{style}]› {msg}[/{style}]")

def ui_user(text):
    con.print()
    con.print(Panel(
        Text(text, style="bold white"),
        title="[green]You[/green]",
        title_align="left",
        border_style="green",
        box=box.ROUNDED,
        padding=(0, 2),
    ))

def ui_ai(text):
    con.print(Panel(
        Text(text, style="white"),
        title=f"[cyan]{ASSISTANT_NAME}[/cyan]",
        title_align="right",
        border_style="cyan",
        box=box.ROUNDED,
        padding=(0, 2),
    ))
    con.print()

def ui_error(msg):
    con.print(f"  [bold red]error: {msg}[/bold red]")

# ============================================================
#  PERSISTENT MEMORY SYSTEM
# ============================================================

MEMORY_FILE = "assets/conversation_history.json"

def _ensure_memory_dir():
    os.makedirs("assets", exist_ok=True)

def save_conversation(memory_list):
    """Save conversation to disk."""
    try:
        _ensure_memory_dir()
        snapshot = {
            "timestamp": dt.now().isoformat(),
            "messages": memory_list
        }
        with open(MEMORY_FILE, "w", encoding="utf-8") as f:
            json.dump(snapshot, f, indent=2, ensure_ascii=False)
        logger.info(f"Saved {len(memory_list)} messages to memory")
    except Exception as e:
        logger.error(f"Failed to save conversation: {e}")

def load_conversation():
    """Load previous conversation from disk."""
    try:
        if os.path.exists(MEMORY_FILE):
            with open(MEMORY_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                logger.info(f"Loaded {len(data.get('messages', []))} messages from disk")
                return data.get('messages', [])
    except Exception as e:
        logger.error(f"Failed to load conversation: {e}")
    return []

def clear_memory_file():
    """Delete persistent memory."""
    try:
        if os.path.exists(MEMORY_FILE):
            os.remove(MEMORY_FILE)
            logger.info("Conversation history cleared")
    except Exception as e:
        logger.error(f"Failed to clear memory: {e}")

# ============================================================
#  INTERRUPT CORE SYSTEM
# ============================================================

_interrupted = threading.Event()
_stop_listening_fn = None
_interrupt_lock = threading.Lock()

def interrupt_trigger():
    """Set interrupt flag."""
    _interrupted.set()
    if pygame.mixer.get_init() and pygame.mixer.music.get_busy():
        pygame.mixer.music.stop()

def interrupt_was_triggered():
    return _interrupted.is_set()

def interrupt_clear():
    _interrupted.clear()

def _interrupt_callback(recognizer, audio):
    """Callback for interrupt listener."""
    try:
        text = recognizer.recognize_google(audio).strip().lower()
        if any(w in text for w in WAKE_TRIGGERS):
            ui_status(f"Interrupt Wake Word Hit: '{text}'", style="bold red")
            interrupt_trigger()
    except Exception:
        pass

def start_interrupt_listener():
    """Start listening for interrupts (non-blocking)."""
    global _stop_listening_fn
    with _interrupt_lock:
        if _stop_listening_fn is not None:
            return

        def _start_async():
            try:
                rec = sr.Recognizer()
                rec.energy_threshold = ENERGY_THRESHOLD
                rec.dynamic_energy_threshold = True
                mic = sr.Microphone()
                global _stop_listening_fn
                _stop_listening_fn = rec.listen_in_background(mic, _interrupt_callback, phrase_time_limit=3)
                logger.debug("Interrupt listener started")
            except Exception as e:
                logger.error(f"Failed to start interrupt listener: {e}")

        t = threading.Thread(target=_start_async, daemon=True)
        t.start()

def stop_interrupt_listener():
    """Stop interrupt listener."""
    global _stop_listening_fn
    with _interrupt_lock:
        if _stop_listening_fn is not None:
            _stop_listening_fn(wait_for_stop=False)
            _stop_listening_fn = None
            time.sleep(0.2)
            logger.debug("Interrupt listener stopped")

# ============================================================
#  VOICE INPUT SYSTEM
# ============================================================

_rec = sr.Recognizer()
_rec.energy_threshold = ENERGY_THRESHOLD
_rec.dynamic_energy_threshold = True
_rec.pause_threshold = 1.5

def listen_to_mic(timeout_duration, phrase_duration):
    """Listen to microphone and return text."""
    try:
        with sr.Microphone() as mic:
            audio = _rec.listen(mic, timeout=timeout_duration, phrase_time_limit=phrase_duration)
        text = _rec.recognize_google(audio).strip()
        return text
    except (sr.UnknownValueError, sr.WaitTimeoutError):
        return None
    except sr.RequestError as e:
        logger.error(f"Speech API Error: {e}")
        return None
    except Exception as e:
        logger.error(f"Mic Error: {e}")
        return None

def listen_for_command():
    """Listen for user command."""
    logger.debug("Listening for command...")
    cmd = listen_to_mic(CMD_TIMEOUT, CMD_PHRASE)
    if cmd:
        logger.info(f"Command heard: {cmd}")
    return cmd

# ============================================================
#  TEXT-TO-SPEECH SYSTEM
# ============================================================

pygame.mixer.init()

def speak(text):
    """Speak text synchronously."""
    if not text:
        return
    logger.debug(f"speak() called with: {text[:50]}...")
    ui_ai(text)

    _TEMP = "temp_sync.mp3"
    try:
        logger.debug("Getting event loop...")
        try:
            loop = asyncio.get_event_loop()
            if loop.is_closed():
                raise RuntimeError("Event loop is closed")
        except (RuntimeError, DeprecationWarning):
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

        logger.debug(f"Creating TTS with voice: {TTS_VOICE}")
        comm = edge_tts.Communicate(text, TTS_VOICE)

        logger.debug(f"Saving TTS to {_TEMP}...")
        loop.run_until_complete(comm.save(_TEMP))
        file_size = os.path.getsize(_TEMP)
        logger.debug(f"TTS file saved, size: {file_size} bytes")

        logger.debug("Starting interrupt listener...")
        start_interrupt_listener()

        logger.debug("Loading audio into pygame mixer...")
        pygame.mixer.music.load(_TEMP)

        logger.debug("Starting playback...")
        pygame.mixer.music.play()
        logger.info(f"Playing audio: {text[:50]}...")

        play_count = 0
        while pygame.mixer.music.get_busy():
            play_count += 1
            if interrupt_was_triggered():
                logger.info("Playback interrupted")
                pygame.mixer.music.stop()
                break
            time.sleep(0.1)
            if play_count > 2000:
                logger.warning("Playback timeout")
                break

        logger.debug("Playback finished, unloading...")
        pygame.mixer.music.unload()
        logger.debug("Audio playback complete")

        try:
            os.remove(_TEMP)
            logger.debug("Temp file deleted")
        except OSError as e:
            logger.warning(f"Could not delete temp file: {e}")

    except Exception as e:
        logger.error(f"Speech synthesis error: {type(e).__name__}: {e}")
        ui_error(f"Speech failed: {e}")
    finally:
        try:
            stop_interrupt_listener()
        except Exception as e:
            logger.error(f"Error stopping interrupt listener: {e}")

def speak_stream(sentence_generator):
    """Stream sentences with TTS."""
    try:
        loop = asyncio.get_event_loop()
        if loop.is_closed():
            raise RuntimeError("Event loop is closed")
    except (RuntimeError, DeprecationWarning):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

    ui_status("Synthesizing and playing...", style="dim cyan")
    full_str = ""
    f_idx = 0
    logger.debug("Starting speak_stream")

    start_interrupt_listener()
    try:
        for sentence in sentence_generator:
            if interrupt_was_triggered():
                logger.info("speak_stream interrupted")
                break

            sentence = sentence.strip()
            if not sentence:
                continue

            full_str += sentence + " "
            tf = f"temp_stream_{f_idx}.mp3"
            f_idx = f_idx + 1

            try:
                logger.debug(f"Synthesizing: {sentence[:40]}...")
                comm = edge_tts.Communicate(sentence, TTS_VOICE)
                loop.run_until_complete(comm.save(tf))
                logger.debug(f"Saved to {tf}")

                logger.debug(f"Loading {tf} into mixer")
                pygame.mixer.music.load(tf)
                pygame.mixer.music.play()
                logger.info(f"Playing: {sentence[:50]}...")

                while pygame.mixer.music.get_busy():
                    if interrupt_was_triggered():
                        pygame.mixer.music.stop()
                        break
                    time.sleep(0.1)

                logger.debug(f"Finished playing {tf}, unloading")
                pygame.mixer.music.unload()
                try:
                    os.remove(tf)
                except OSError as e:
                    logger.warning(f"Could not delete {tf}: {e}")
            except Exception as e:
                logger.error(f"Error playing sentence: {e}")
    finally:
        try:
            stop_interrupt_listener()
        except Exception as e:
            logger.error(f"Error stopping interrupt listener: {e}")

    if full_str.strip():
        text = full_str.strip()
        if interrupt_was_triggered():
            text += " [Interrupted...]"
        ui_ai(text)
        logger.info(f"Stream complete")

# ============================================================
#  AI BRAIN SYSTEM
# ============================================================

_mem = [{"role": "system", "content": AI_PROMPT}]
if PERSIST_MEMORY:
    try:
        persisted = load_conversation()
        if persisted and len(persisted) > 1:
            _mem = persisted
    except Exception as e:
        logger.error(f"Failed to load persistent memory: {e}")

def _clean_text(t):
    """Clean text for display."""
    for a, b in {"\u2018": "'", "\u2019": "'", "\u201c": '"',
                 "\u201d": '"', "\u2013": "-", "\u2014": "-",
                 "\u2026": "...", "\u00a0": " ", "\n": " "}.items():
        t = t.replace(a, b)
    return t.encode("ascii", "ignore").decode("ascii")

def ai_ask_stream(question):
    """Ask AI and stream responses."""
    _mem.append({"role": "user", "content": question})
    while len(_mem) > MAX_MEMORY + 1:
        _mem.pop(1)

    full_answer = ""
    try:
        logger.debug(f"Sending request to AI: {question}")
        r = requests.post(AI_URL, json={"messages": list(_mem)}, timeout=20)
        r.raise_for_status()

        try:
            response_json = r.json()
            if isinstance(response_json, list):
                if "message" in response_json[0]:
                    full_answer = response_json[0]["message"]["content"]
                else:
                    full_answer = str(response_json[0])
            elif "choices" in response_json:
                full_answer = response_json["choices"][0]["message"]["content"]
            else:
                full_answer = response_json.get("response", response_json.get("text", str(response_json)))
        except requests.exceptions.JSONDecodeError:
            full_answer = r.text

        full_answer = _clean_text(full_answer.strip())
        logger.info(f"AI Response: {full_answer[:100]}...")

        for sentence in full_answer.split('. '):
            if sentence:
                yield sentence.strip() + "."

        _mem.append({"role": "assistant", "content": full_answer})

        if PERSIST_MEMORY:
            try:
                save_conversation(_mem)
            except Exception as e:
                logger.error(f"Failed to save conversation: {e}")

    except requests.Timeout:
        logger.warning("AI API timeout")
        yield "I couldn't reach my brain in time. Could you ask again?"
    except requests.ConnectionError:
        logger.warning("No internet connection")
        yield "I'm offline right now. Could you ask me something simpler or check your internet?"
    except Exception as e:
        logger.error(f"AI fetch error: {e}")
        ui_error(f"AI Error: {e}")
        yield "Something went wrong while thinking. Please try again."

def ai_ask(question):
    """Synchronous AI query."""
    sentences = list(ai_ask_stream(question))
    return " ".join(sentences)

def ai_forget():
    """Clear memory."""
    global _mem
    _mem.clear()
    _mem.append({"role": "system", "content": AI_PROMPT})
    if PERSIST_MEMORY:
        clear_memory_file()
    logger.info("Memory cleared")

# ============================================================
#  WEATHER SYSTEM
# ============================================================

def get_weather(city="current location"):
    """Fetch weather info."""
    try:
        logger.debug(f"Fetching weather for {city}")
        if city.lower() == "current location":
            r = requests.get("https://wttr.in/?format=j1", timeout=5)
            data = r.json()
            current = data["current_condition"][0]
            temp = current["temp_C"]
            desc = current["weatherDesc"][0]["value"]
            return f"It's {temp} degrees and {desc}."
        else:
            r = requests.get(f"https://wttr.in/{city}?format=j1", timeout=5)
            data = r.json()
            current = data["current_condition"][0]
            temp = current["temp_C"]
            desc = current["weatherDesc"][0]["value"]
            return f"In {city}, it's {temp} degrees and {desc}."
    except Exception as e:
        logger.error(f"Weather fetch failed: {e}")
        return "I couldn't fetch the weather. Check your internet connection."

# ============================================================
#  COMMAND HANDLER
# ============================================================

def handle_command(cmd_raw):
    """Process voice commands."""
    c = cmd_raw.lower().strip()
    logger.info(f"Command received: {c}")

    # Media Control
    if "volume up" in c:
        logger.debug("Volume up")
        for _ in range(5):
            pyautogui.press("volumeup")
        return speak("Volume up.")
    if "volume down" in c:
        logger.debug("Volume down")
        for _ in range(5):
            pyautogui.press("volumedown")
        return speak("Volume down.")
    if "mute" in c:
        logger.debug("Mute")
        pyautogui.press("volumemute")
        return speak("Muted.")
    if "pause" in c or ("play" in c and "youtube" not in c and not c.startswith("play ")):
        logger.debug("Play/pause")
        pyautogui.press("playpause")
        return
    if "next track" in c or "next song" in c:
        logger.debug("Next track")
        pyautogui.press("nexttrack")
        return

    # Window Control
    if "close window" in c or "close this" in c:
        logger.debug("Close window")
        pyautogui.hotkey("alt", "f4")
        return speak("Closing.")
    if "minimize" in c:
        logger.debug("Minimize")
        pyautogui.hotkey("win", "down")
        return

    # Text Input
    if c.startswith("type "):
        text = cmd_raw[5:].strip()
        if text:
            logger.debug(f"Typing: {text}")
            keyboard.write(text)
        return
    if "press enter" in c:
        logger.debug("Press enter")
        keyboard.press_and_release("enter")
        return

    # Website Launch
    for name, url in WEBSITES.items():
        if f"open {name}" in c:
            logger.info(f"Opening {name}")
            webbrowser.open(url)
            return speak(f"Opening {name.title()}.")

    # Music Library
    for song_name, url in MUSIC_LIBRARY.items():
        if f"play {song_name}" in c:
            logger.info(f"Playing {song_name}")
            webbrowser.open(url)
            return speak(f"Playing {song_name}.")

    # Utilities
    if "time" in c and ("what" in c or "tell" in c):
        current_time = dt.now().strftime('%I:%M %p')
        logger.debug(f"Telling time: {current_time}")
        return speak(f"It is {current_time}.")

    if "joke" in c:
        logger.debug("Telling joke")
        return speak(pyjokes.get_joke())

    if "screenshot" in c:
        logger.info("Taking screenshot")
        os.makedirs("assets/screenshots", exist_ok=True)
        ts = dt.now().strftime("%Y%m%d_%H%M%S")
        pyautogui.screenshot().save(f"assets/screenshots/{ts}.png")
        return speak("Screenshot saved.")

    # Weather
    if "weather" in c:
        city = "current location"
        for word in c.split():
            if word not in ("what's", "what", "is", "the", "weather", "in", "tell", "me"):
                if len(word) > 2:
                    city = word
                    break
        logger.info(f"Fetching weather for {city}")
        weather_info = get_weather(city)
        return speak(weather_info)

    # YouTube Play
    if c.startswith("play "):
        q = c[5:].strip()
        logger.info(f"Playing on YouTube: {q}")
        webbrowser.open(f"https://www.youtube.com/results?search_query={q.replace(' ', '+')}")
        return speak(f"Playing {q}.")

    # Memory Management
    if "forget" in c or "reset" in c or "clear memory" in c:
        logger.info("Clearing memory")
        ai_forget()
        return speak("Memory cleared.")

    if c in ("exit", "stop", "quit", "bye", "goodbye", "thank you"):
        goodbye = "Thank you for using Amulya AI. Goodbye!"
        try:
            speak(goodbye)
        except Exception as e:
            logger.error(f"Failed to speak goodbye: {e}")
        logger.info("User exiting")
        exit()

    # AI Fallback
    ui_status("Thinking...", style="dim cyan")
    logger.debug("Querying AI brain")
    sentences = ai_ask_stream(cmd_raw)
    speak_stream(sentences)

# ============================================================
#  MAIN DIALOGUE SYSTEM
# ============================================================

def background_interrupt_listener():
    """Listen for wake words in background."""
    bg_rec = sr.Recognizer()
    bg_rec.energy_threshold = ENERGY_THRESHOLD
    bg_rec.dynamic_energy_threshold = True

    try:
        with sr.Microphone() as bg_mic:
            while True:
                try:
                    audio = bg_rec.listen(bg_mic, timeout=1, phrase_time_limit=3)
                    text = bg_rec.recognize_google(audio).strip().lower()
                    if any(w in text for w in WAKE_TRIGGERS):
                        ui_status("Interrupt Triggered", style="bold red")
                        interrupt_trigger()
                except (sr.WaitTimeoutError, sr.UnknownValueError):
                    pass
                except sr.RequestError as e:
                    logger.error(f"Background STT Error: {e}")
                    time.sleep(1)
    except Exception as e:
        logger.error(f"Mic hardware issue: {e}")

def start_conversation():
    """Main dialogue loop."""
    introductions = [
        "Hey there! I'm Amulya AI, your intelligent voice assistant. I can answer questions, search the web, play music, and much more. What can I help you with today?",
        "Hi! I'm Amulya, your AI assistant. I'm here to help you with anything you need - from answering questions to controlling your computer. What would you like to know?",
        "Hello! I'm Amulya AI. I can assist you with information, web searches, tasks, and more. What's on your mind?"
    ]

    follow_ups = [
        "Is there anything else I can help you with?",
        "Do you have any other questions?",
        "What else would you like to know?",
        "Anything else you'd like help with?"
    ]

    prompt_messages = [
        "What can I help you with?",
        "Go ahead, I'm listening.",
        "Tell me something.",
        "What would you like to ask?"
    ]

    # Start background listener
    t = threading.Thread(target=background_interrupt_listener, daemon=True)
    t.start()
    logger.info("Background interrupt listener started")

    # Introduce
    try:
        intro = random.choice(introductions)
        logger.info(f"Speaking introduction")
        speak(intro)
        logger.info("Introduction spoken successfully")
    except Exception as e:
        logger.error(f"Failed to speak introduction: {e}")
        ui_error(f"Speech failed: {e}")

    # Main loop
    while True:
        try:
            interrupt_clear()

            ui_status("Listening...", style="cyan")
            logger.debug("Waiting for user input")
            question = listen_for_command()

            if not question:
                ui_status("No input heard. Try again.", style="dim default")
                logger.debug("No input received")
                time.sleep(1)
                ui_status("Listening...", style="cyan")
                continue

            ui_user(question)
            logger.info(f"User asked: {question}")

            # Exit commands
            if question.lower().strip() in ("exit", "stop", "quit", "bye", "goodbye", "thank you"):
                goodbye = "Thank you for using Amulya AI. Goodbye!"
                try:
                    speak(goodbye)
                except Exception as e:
                    logger.error(f"Failed to speak goodbye: {e}")
                logger.info("User initiated exit")
                exit()

            # Handle command
            try:
                logger.debug(f"Handling command: {question[:50]}...")
                handle_command(question)
            except Exception as e:
                logger.error(f"Failed to handle command: {e}")
                ui_error(f"Command error: {e}")

            # Follow-up
            try:
                if not interrupt_was_triggered():
                    speak(random.choice(follow_ups))
                    interrupt_clear()
                else:
                    interrupt_clear()
                    ui_status("Bouncing back to listening...", style="bold green")
                    speak(random.choice(prompt_messages))
            except Exception as e:
                logger.error(f"Failed to speak follow-up: {e}")

        except KeyboardInterrupt:
            logger.info("KeyboardInterrupt - exiting")
            break
        except Exception as e:
            logger.error(f"Unexpected error in dialogue loop: {e}")
            ui_error(f"Loop error: {e}")
            time.sleep(1)

# ============================================================
#  MAIN ENTRY POINT
# ============================================================

def main():
    try:
        logger.info("=" * 43)
        logger.info(f"Starting {ASSISTANT_NAME}")
        logger.info("=" * 43)
        ui_banner()
        start_conversation()
    except Exception as e:
        logger.critical(f"Fatal error: {e}")
        ui_error(f"Fatal error: {e}")
        print(f"FATAL ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()

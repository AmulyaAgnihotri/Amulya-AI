# ============================================================
#  commands.py  —  Lean Voice Command Router
# ============================================================
import webbrowser, datetime, subprocess, os
import json
from urllib import request as urlrequest
import pyjokes         # pyre-ignore[21]
import pyautogui       # pyre-ignore[21]
import keyboard        # pyre-ignore[21]
import logger          # pyre-ignore[21]
from config import WEBSITES  # pyre-ignore[21]
from speech_engine import speak, speak_stream  # pyre-ignore[21]
from musicLibrary import music  # pyre-ignore[21]
import ai_brain  # pyre-ignore[21]
import ui        # pyre-ignore[21]


def _get_json(url, timeout=5):
    req = urlrequest.Request(url, headers={"User-Agent": "AmulyaAI/1.0"})
    with urlrequest.urlopen(req, timeout=timeout) as resp:
        charset = resp.headers.get_content_charset() or "utf-8"
        return json.loads(resp.read().decode(charset, errors="replace"))


def get_weather(city="current location"):
    """Fetch weather using free API."""
    try:
        logger.debug(f"Fetching weather for {city}")
        if city.lower() == "current location":
            # Try to get local IP weather without API key
            data = _get_json("https://wttr.in/?format=j1", timeout=5)
            current = data["current_condition"][0]
            temp = current["temp_C"]
            desc = current["weatherDesc"][0]["value"]
            return f"It's {temp} degrees and {desc}."
        else:
            data = _get_json(f"https://wttr.in/{city}?format=j1", timeout=5)
            current = data["current_condition"][0]
            temp = current["temp_C"]
            desc = current["weatherDesc"][0]["value"]
            return f"In {city}, it's {temp} degrees and {desc}."
    except Exception as e:
        logger.error(f"Weather fetch failed: {e}")
        return "I couldn't fetch the weather. Check your internet connection."


def handle(cmd_raw):
    """Processes user voice commands cleanly."""
    c = cmd_raw.lower().strip()
    logger.info(f"Command received: {c}")

    # ── Media ──
    if "volume up" in c:
        logger.debug("Volume up")
        for _ in range(5): pyautogui.press("volumeup")
        return speak("Volume up.")
    if "volume down" in c:
        logger.debug("Volume down")
        for _ in range(5): pyautogui.press("volumedown")
        return speak("Volume down.")
    if "mute" in c:
        logger.debug("Mute")
        pyautogui.press("volumemute")
        return speak("Muted.")
    if "pause" in c or "play" in c and "youtube" not in c and not c.startswith("play "):
        logger.debug("Play/pause toggle")
        pyautogui.press("playpause")
        return
    if "next track" in c or "next song" in c:
        logger.debug("Next track")
        pyautogui.press("nexttrack")
        return

    # ── Windows ──
    if "close window" in c or "close this" in c:
        logger.debug("Close window")
        pyautogui.hotkey("alt", "f4")
        return speak("Closing.")
    if "minimize" in c:
        logger.debug("Minimize window")
        pyautogui.hotkey("win", "down")
        return

    # ── Dictation ──
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

    # ── Quick Launch ──
    for name, url in WEBSITES.items():
        if f"open {name}" in c:
            logger.info(f"Opening {name}")
            webbrowser.open(url)
            return speak(f"Opening {name.title()}.")

    # ── Music Library ──
    for song_name, url in music.items():
        if f"play {song_name}" in c:
            logger.info(f"Playing {song_name}")
            webbrowser.open(url)
            return speak(f"Playing {song_name}.")

    # ── Utils ──
    if "time" in c and ("what" in c or "tell" in c):
        current_time = datetime.datetime.now().strftime('%I:%M %p')
        logger.debug(f"Telling time: {current_time}")
        return speak(f"It is {current_time}.")
    
    if "joke" in c:
        logger.debug("Telling joke")
        return speak(pyjokes.get_joke())
    
    if "screenshot" in c:
        logger.info("Taking screenshot")
        os.makedirs("assets/screenshots", exist_ok=True)
        ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        pyautogui.screenshot().save(f"assets/screenshots/{ts}.png")
        return speak("Screenshot saved.")

    # ── Weather ──
    if "weather" in c:
        # Extract city if mentioned
        city = "current location"
        for word in c.split():
            if word not in ("what's", "what", "is", "the", "weather", "in", "tell", "me"):
                if len(word) > 2:
                    city = word
                    break
        logger.info(f"Fetching weather for {city}")
        weather_info = get_weather(city)
        return speak(weather_info)

    # ── YouTube Play ──
    if c.startswith("play "):
        q = c[5:].strip()
        logger.info(f"Playing on YouTube: {q}")
        webbrowser.open(f"https://www.youtube.com/results?search_query={q.replace(' ', '+')}")
        return speak(f"Playing {q}.")

    # ── Memory ──
    if "forget" in c or "reset" in c or "clear memory" in c:
        logger.info("Clearing memory")
        ai_brain.forget()
        return speak("Memory cleared.")
    
    if c in ("exit", "stop", "quit", "bye", "goodbye"):
        logger.info("Exiting application")
        speak("Goodbye!")
        exit()

    # ── AI API Fallback (Streaming Voice) ──
    ui.status("Thinking...", style="dim cyan")
    logger.debug("Querying AI brain")
    # Tell UI what we asked, stream sentences back instantly
    sentences = ai_brain.ask_stream(cmd_raw)
    speak_stream(sentences)

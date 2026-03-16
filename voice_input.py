# ============================================================
#  voice_input.py  —  Robust Audio Input Manager
# ============================================================
import speech_recognition as sr  # pyre-ignore[21]
import ui                        # pyre-ignore[21]
import logger                    # pyre-ignore[21]
from config import ENERGY_THRESHOLD, WAKE_TIMEOUT, WAKE_PHRASE, CMD_TIMEOUT, CMD_PHRASE, WAKE_TRIGGERS  # pyre-ignore[21]

_rec = sr.Recognizer()
_rec.energy_threshold = ENERGY_THRESHOLD
_rec.dynamic_energy_threshold = True
_rec.pause_threshold = 1.5  # Give the user 1.5s pause to think


def listen(timeout_duration, phrase_duration):
    """Listen to microphone and return recognized text (or None if silence)."""
    try:
        with sr.Microphone() as mic:
            audio = _rec.listen(mic, timeout=timeout_duration, phrase_time_limit=phrase_duration)
        text = _rec.recognize_google(audio).strip()
        return text
    except (sr.UnknownValueError, sr.WaitTimeoutError):
        return None
    except sr.RequestError as e:
        ui.error(f"Speech API Error: {e}")
        return None
    except Exception as e:
        ui.error(f"Mic Error: {e}")
        return None


def listen_for_wake_word():
    """Single pass listening specifically tuned for wake words."""
    text = listen(WAKE_TIMEOUT, WAKE_PHRASE)
    if text:
        text_lower = text.lower()
        logger.debug(f"Wake word check: '{text}'")
        if any(w in text_lower for w in WAKE_TRIGGERS):
            logger.info(f"Wake word detected: {text}")
            return True
    return False


def listen_for_command():
    """Listens for the user's actual question/command."""
    logger.debug("Listening for command...")
    cmd = listen(CMD_TIMEOUT, CMD_PHRASE)
    if cmd:
        logger.info(f"Command heard: {cmd}")
    return cmd

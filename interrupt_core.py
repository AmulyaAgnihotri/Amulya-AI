# ============================================================
#  interrupt_core.py  —  Exclusive Hardware Interrupt Listener
# ============================================================
import threading
import time
import pygame  # pyre-ignore[21]
import speech_recognition as sr  # pyre-ignore[21]
import ui      # pyre-ignore[21]
from config import ENERGY_THRESHOLD, WAKE_TRIGGERS  # pyre-ignore[21]

_interrupted = threading.Event()
_stop_listening_fn = None
_lock = threading.Lock()


def trigger():
    """Sets the interrupt flag and halts playback."""
    _interrupted.set()
    if pygame.mixer.get_init() and pygame.mixer.music.get_busy():
        pygame.mixer.music.stop()

def was_interrupted():
    return _interrupted.is_set()

def clear():
    _interrupted.clear()

def _listen_callback(recognizer, audio):
    """Callback fired by background listener when audio is gathered."""
    try:
        text = recognizer.recognize_google(audio).strip().lower()
        if any(w in text for w in WAKE_TRIGGERS):
            ui.status(f"Interrupt Wake Word Hit: '{text}'", style="bold red")
            trigger()
    except Exception:
        pass


def start_interrupt_listener():
    """Starts listening exclusively while AI is speaking."""
    global _stop_listening_fn
    with _lock:
        if _stop_listening_fn is not None:
            return  # Already running
        
        # Start in a separate thread to avoid blocking
        def _start_async():
            try:
                rec = sr.Recognizer()
                rec.energy_threshold = ENERGY_THRESHOLD
                rec.dynamic_energy_threshold = True
                mic = sr.Microphone()
                
                # Skip ambient noise calibration to avoid blocking
                # It's already handled in voice_input.py
                
                # Starts a daemon thread that feeds audio to _listen_callback
                global _stop_listening_fn
                _stop_listening_fn = rec.listen_in_background(mic, _listen_callback, phrase_time_limit=3)
            except Exception as e:
                ui.error(f"Failed to start interrupt hook: {e}")
        
        t = threading.Thread(target=_start_async, daemon=True)
        t.start()


def stop_interrupt_listener():
    """Releases the microphone lock."""
    global _stop_listening_fn
    with _lock:
        if _stop_listening_fn is not None:
            _stop_listening_fn(wait_for_stop=False)
            _stop_listening_fn = None
            # Tiny sleep to ensure the hardware audio device lock is released by pyaudio
            time.sleep(0.2)

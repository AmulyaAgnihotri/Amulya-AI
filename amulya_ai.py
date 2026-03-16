# ============================================================
#  amulya_ai.py  —  The Seamless Real-Time Dialogue Loop
# ============================================================
import threading
import time
import random
import config
import logger                                # pyre-ignore[21]
from speech_engine import speak            # pyre-ignore[21]
from voice_input import listen_for_wake_word, listen_for_command  # pyre-ignore[21]
from commands import handle                # pyre-ignore[21]
import ui                                  # pyre-ignore[21]
import interrupt_core                      # pyre-ignore[21]


def background_interrupt_listener():
    """ 
    Runs continuously in a separate daemon thread.
    Constantly listens for the wake word ('Hey Amulya').
    If heard while the AI is talking, it sets the global interrupt!
    """
    import speech_recognition as sr
    bg_rec = sr.Recognizer()
    bg_rec.energy_threshold = config.ENERGY_THRESHOLD
    bg_rec.dynamic_energy_threshold = True

    try:
        with sr.Microphone() as bg_mic:
            while True:
                # Short listen bursts
                try:
                    audio = bg_rec.listen(bg_mic, timeout=1, phrase_time_limit=3)
                    text = bg_rec.recognize_google(audio).strip().lower()
                    if any(w in text for w in config.WAKE_TRIGGERS):
                        ui.status("Interrupt Triggered", style="bold red")
                        interrupt_core.trigger()
                except (sr.WaitTimeoutError, sr.UnknownValueError):
                    pass
                except sr.RequestError as e:
                    ui.error(f"Background STT Error: {e}")
                    time.sleep(1) # Prevent tight crash loop
    except Exception as e:
        ui.error(f"Mic hardware issue: {e}")


def wait_for_activation():
    """Blocks until the user says a wake word (Hey Amulya)."""
    ui.status("Sleeping (Awaiting Wake Word)...", style="magenta")
    while True:
        # Check standard microphone capture...
        if listen_for_wake_word():
            return True


def start_dialogue_node():
    """The central loop handling fluent conversation."""
    
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

    # Spawn background daemon so user can interrupt TTS at any time
    t = threading.Thread(target=background_interrupt_listener, daemon=True)
    t.start()
    logger.info("Background interrupt listener started")
    
    # Introduce immediately at startup
    try:
        intro = random.choice(introductions)
        logger.info(f"Speaking introduction: {intro[:50]}...")
        speak(intro)
        logger.info("Introduction spoken successfully")
    except Exception as e:
        logger.error(f"Failed to speak introduction: {e}")
        ui.error(f"Speech failed: {e}")
        print(f"SPEECH ERROR: {e}")
    
    # Main conversation loop
    while True:
        try:
            interrupt_core.clear()
            
            # Show waiting for input status
            ui.status("Listening...", style="cyan")
            logger.debug("Waiting for user input")
            question = listen_for_command()
            
            if not question:
                ui.status("No input heard. Try again.", style="dim default")
                logger.debug("No input received")
                time.sleep(1)
                ui.status("Listening...", style="cyan")
                continue

            ui.user(question)
            logger.info(f"User asked: {question}")
            
            # Check for exit commands
            if question.lower().strip() in ("exit", "stop", "quit", "bye", "goodbye", "thank you"):
                try:
                    speak("Thank you for using Amulya AI. Goodbye!")
                except Exception as e:
                    logger.error(f"Failed to speak goodbye: {e}")
                logger.info("User initiated exit")
                exit()
            
            # Handle the command (could be AI question, voice command, etc.)
            try:
                logger.debug(f"Handling command: {question[:50]}...")
                handle(question)
            except Exception as e:
                logger.error(f"Failed to handle command: {e}")
                ui.error(f"Command error: {e}")
            
            # Ask for follow-up
            try:
                if not interrupt_core.was_interrupted():
                    speak(random.choice(follow_ups))
                    interrupt_core.clear()
                else:
                    # User interrupted by saying wake word again
                    interrupt_core.clear()
                    ui.status("Bouncing back to listening...", style="bold green")
                    speak(random.choice(prompt_messages))
            except Exception as e:
                logger.error(f"Failed to speak follow-up: {e}")
        
        except KeyboardInterrupt:
            logger.info("KeyboardInterrupt - exiting")
            break
        except Exception as e:
            logger.error(f"Unexpected error in dialogue loop: {e}")
            ui.error(f"Loop error: {e}")
            time.sleep(1)


def main():
    logger.info("=" * 43)
    logger.info(f"Starting {config.ASSISTANT_NAME}")
    logger.info("=" * 43)
    ui.banner()
    start_dialogue_node()


if __name__ == "__main__":
    main()

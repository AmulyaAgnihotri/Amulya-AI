import os
import pvporcupine      # pyre-ignore[21]
from pvrecorder import PvRecorder  # pyre-ignore[21]
import interrupt_core   # pyre-ignore[21]
import ui               # pyre-ignore[21]

class WakeWordEngine:
    def __init__(self):
        # The user must add this to their .env file to use Porcupine
        self.access_key = os.getenv("PICOVOICE_ACCESS_KEY")
        self.porcupine = None
        self.recorder = None
        
        if self.access_key:
            try:
                # Fallback to 'jarvis' as the pre-trained built-in keyword
                # To use "Hey Amulya", the user must download a custom .ppn file 
                # from the Picovoice console and pass its path via `keyword_paths`.
                self.porcupine = pvporcupine.create(
                    access_key=self.access_key,
                    keywords=['jarvis', 'computer']
                )
                self.recorder = PvRecorder(device_index=-1, frame_length=self.porcupine.frame_length)  # pyre-ignore[16]
                ui.status("Picovoice Porcupine Wake Word Engine: ONLINE", style="bold green")
            except Exception as e:
                ui.error(f"Porcupine Init Error: {e}")
                self.porcupine = None
        else:
            ui.status(
                "Notice: No PICOVOICE_ACCESS_KEY found in .env. "
                "Falling back to basic speech recognition for wake word. "
                "Get a free key at picovoice.ai to use Porcupine offline detection.",
                style="yellow"
            )

    def listen_for_wake_word_blocking(self):
        """
        Blocks until the wake word is detected using the hardware audio stream.
        """
        if not self.porcupine or not self.recorder:
            # Fallback to older Google STT listen method if Porcupine wasn't set up
            from voice_input import listen, is_wake  # pyre-ignore[21]
            while True:
                text = listen(timeout=5, phrase_limit=3)
                if is_wake(text):
                    interrupt_core.trigger_interruption()
                    return True
            
        try:
            self.recorder.start()  # pyre-ignore[16]
            while True:
                pcm = self.recorder.read()  # pyre-ignore[16]
                keyword_index = self.porcupine.process(pcm)  # pyre-ignore[16]
                
                # If a keyword is detected!
                if keyword_index >= 0:
                    interrupt_core.trigger_interruption()
                    return True

        except Exception as e:
            ui.error(f"Porcupine Audio Error: {e}")
            return False
            
        finally:
            self.recorder.stop()  # pyre-ignore[16]

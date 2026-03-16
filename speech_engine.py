# ============================================================
#  speech_engine.py  —  High-Performance Seamless Voice Synthesis
# ============================================================
import os
import asyncio
import pygame      # pyre-ignore[21]
import edge_tts    # pyre-ignore[21]
import ui          # pyre-ignore[21]
import logger      # pyre-ignore[21]
import interrupt_core  # pyre-ignore[21]
from config import TTS_VOICE # pyre-ignore[21]

pygame.mixer.init()

def speak(text):
    """Speaks short prompts synchronously, with interruption hook."""
    if not text:
        return
    logger.debug(f"speak() called with: {text[:50]}...")
    ui.ai(text)
    
    _TEMP = "temp_sync.mp3"
    try:
        logger.debug("Getting event loop...")
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        
        logger.debug(f"Creating TTS with voice: {TTS_VOICE}")
        comm = edge_tts.Communicate(text, TTS_VOICE)
        
        logger.debug(f"Saving TTS to {_TEMP}...")
        loop.run_until_complete(comm.save(_TEMP))
        file_size = os.path.getsize(_TEMP)
        logger.debug(f"TTS file saved, size: {file_size} bytes")
        
        logger.debug("Starting interrupt listener...")
        interrupt_core.start_interrupt_listener()
        
        logger.debug("Loading audio into pygame mixer...")
        pygame.mixer.music.load(_TEMP)
        
        logger.debug("Starting playback...")
        pygame.mixer.music.play()
        logger.info(f"Playing audio: {text[:50]}...")
        
        # Play and watch for interruption
        play_count = 0
        while pygame.mixer.music.get_busy():
            play_count += 1
            if interrupt_core.was_interrupted():
                logger.info("Playback interrupted")
                pygame.mixer.music.stop()
                break
            import time
            time.sleep(0.1)  # Check every 100ms instead of 30fps
            if play_count > 2000:  # Safety timeout (200 seconds)
                logger.warning("Playback timeout - stopping")
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
        ui.error(f"Speech failed: {e}")
        print(f"SPEECH ERROR: {type(e).__name__}: {e}")
    finally:
        try:
            interrupt_core.stop_interrupt_listener()
        except Exception as e:
            logger.error(f"Error stopping interrupt listener: {e}")


def speak_stream(sentence_generator):
    """Streams sentences progressively with deep interruption hooks."""
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

    ui.status("Synthesizing and playing...", style="dim cyan")
    full_str = ""
    f_idx = 0
    logger.debug("Starting speak_stream")

    interrupt_core.start_interrupt_listener()
    try:
        for sentence in sentence_generator:
            if interrupt_core.was_interrupted():
                logger.info("speak_stream interrupted")
                break
                
            sentence = sentence.strip()
            if not sentence: 
                continue
            
            full_str += sentence + " "
            tf = f"temp_stream_{f_idx}.mp3"
            f_idx = f_idx + 1  # pyre-ignore[16, 58]

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
                    if interrupt_core.was_interrupted():
                        pygame.mixer.music.stop()
                        break
                    pygame.time.Clock().tick(30)
                
                logger.debug(f"Finished playing {tf}, unloading")    
                pygame.mixer.music.unload()
                try: 
                    os.remove(tf)
                except OSError as e:
                    logger.warning(f"Could not delete {tf}: {e}")
            except Exception as e:
                logger.error(f"Error playing sentence '{sentence[:40]}...': {e}")
                print(f"STREAM ERROR: {type(e).__name__}: {e}")
    finally:
        try:
            interrupt_core.stop_interrupt_listener()
        except Exception as e:
            logger.error(f"Error stopping interrupt listener: {e}")

    if full_str.strip():
        text = full_str.strip()
        if interrupt_core.was_interrupted():
            text += " [Interrupted...]"
        ui.ai(text)
        logger.info(f"Stream complete: {text[:100]}...")

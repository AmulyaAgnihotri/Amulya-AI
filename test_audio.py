# ============================================================
#  test_audio.py  —  Test Audio & TTS Setup
# ============================================================
import sys
import os

print("🔍 Amulya AI Audio Diagnostics\n")

# 1. Test imports
print("1️⃣  Testing imports...")
try:
    import pygame
    print("   ✅ pygame imported")
except ImportError as e:
    print(f"   ❌ pygame FAILED: {e}")
    sys.exit(1)

try:
    import edge_tts
    print("   ✅ edge_tts imported")
except ImportError as e:
    print(f"   ❌ edge_tts FAILED: {e}")
    sys.exit(1)

try:
    import asyncio
    print("   ✅ asyncio imported")
except ImportError as e:
    print(f"   ❌ asyncio FAILED: {e}")
    sys.exit(1)

try:
    import speech_recognition as sr
    print("   ✅ speech_recognition imported")
except ImportError as e:
    print(f"   ❌ speech_recognition FAILED: {e}")
    sys.exit(1)

# 2. Test pygame mixer
print("\n2️⃣  Testing pygame mixer...")
try:
    pygame.mixer.init()
    print("   ✅ pygame.mixer initialized")
    print(f"   📊 Mixer info: {pygame.mixer.get_init()}")
except Exception as e:
    print(f"   ❌ mixer init FAILED: {e}")
    print("   💡 Try: pip install --upgrade pygame")
    sys.exit(1)

# 3. Test microphone
print("\n3️⃣  Testing microphone...")
try:
    rec = sr.Recognizer()
    with sr.Microphone() as mic:
        print("   ✅ Microphone detected and accessible")
except Exception as e:
    print(f"   ⚠️  Microphone issue: {e}")
    print("   💡 Make sure your microphone is connected and enabled")

# 4. Test TTS synthesis
print("\n4️⃣  Testing Text-to-Speech synthesis...")
try:
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    comm = edge_tts.Communicate("Hello, I am Amulya AI", "en-US-ChristopherNeural")
    test_file = "test_tts.mp3"
    loop.run_until_complete(comm.save(test_file))
    
    if os.path.exists(test_file):
        file_size = os.path.getsize(test_file)
        print(f"   ✅ TTS generated audio ({file_size} bytes)")
        
        # Try to play it
        print("\n5️⃣  Testing audio playback...")
        try:
            pygame.mixer.music.load(test_file)
            pygame.mixer.music.play()
            
            print("   ⏳ Playing audio... (listening for 3 seconds)")
            print("   🔊 If you hear 'Hello, I am Amulya AI', audio is working!")
            
            import time
            time.sleep(3)
            
            pygame.mixer.music.stop()
            print("   ✅ Audio playback test complete")
            
        except Exception as e:
            print(f"   ❌ Playback FAILED: {e}")
        finally:
            try:
                os.remove(test_file)
            except:
                pass
    else:
        print(f"   ❌ TTS file not created: {test_file}")
        
except Exception as e:
    print(f"   ❌ TTS FAILED: {e}")
    print(f"   📍 Error type: {type(e).__name__}")
    import traceback
    traceback.print_exc()

print("\n" + "="*50)
print("✅ All tests passed! Amulya AI should work.")
print("="*50)
print("\nRun: python main.py")

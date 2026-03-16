# ============================================================
#  persistent_memory.py  —  Conversation History SaveLoad
# ============================================================
import json
import os
from datetime import datetime
import logger

MEMORY_FILE = "assets/conversation_history.json"


def _ensure_dir():
    """Create assets directory if needed."""
    os.makedirs("assets", exist_ok=True)


def save_conversation(memory_list):
    """Save conversation memory to persistent storage."""
    try:
        _ensure_dir()
        snapshot = {
            "timestamp": datetime.now().isoformat(),
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


def clear_memory():
    """Delete persistent memory file."""
    try:
        if os.path.exists(MEMORY_FILE):
            os.remove(MEMORY_FILE)
            logger.info("Conversation history cleared")
    except Exception as e:
        logger.error(f"Failed to clear memory: {e}")

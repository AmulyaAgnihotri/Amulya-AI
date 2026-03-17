# ============================================================
#  ai_brain.py  —  Conversational AI Engine
# ============================================================
import json
import socket
from urllib import request as urlrequest, error as urlerror
import ui        # pyre-ignore[21]
import logger    # pyre-ignore[21]
from config import AI_URL, MAX_MEMORY, AI_PROMPT, PERSIST_MEMORY  # pyre-ignore[21]
from persistent_memory import save_conversation, load_conversation, clear_memory as clear_persistent_memory  # pyre-ignore[21]

# Load persisted memory on startup
_mem = [{"role": "system", "content": AI_PROMPT}]
if PERSIST_MEMORY:
    try:
        persisted = load_conversation()
        if persisted and len(persisted) > 1:  # More than just system prompt
            _mem = persisted
    except Exception as e:
        logger.error(f"Failed to load persistent memory: {e}")


def _clean(t):
    """Strip non-ASCII safely for Windows console."""
    for a, b in {"\u2018": "'", "\u2019": "'", "\u201c": '"',
                 "\u201d": '"', "\u2013": "-", "\u2014": "-",
                 "\u2026": "...", "\u00a0": " ", "\n": " "}.items():
        t = t.replace(a, b)
    return t.encode("ascii", "ignore").decode("ascii")


def _post_json(url, payload, timeout=20):
    data = json.dumps(payload).encode("utf-8")
    req = urlrequest.Request(
        url,
        data=data,
        method="POST",
        headers={
            "Content-Type": "application/json",
            "Accept": "application/json,text/plain,*/*",
            "User-Agent": "AmulyaAI/1.0",
        },
    )
    with urlrequest.urlopen(req, timeout=timeout) as resp:
        charset = resp.headers.get_content_charset() or "utf-8"
        return resp.read().decode(charset, errors="replace")


def ask_stream(question):
    """
    Stream words back, yielding full sentences one by one.
    This lets us speak Sentence 1 while generating Sentence 2.
    Falls back gracefully if offline.
    """
    _mem.append({"role": "user", "content": question})
    while len(_mem) > MAX_MEMORY + 1:
        _mem.pop(1)

    full_answer = ""
    try:
        # We don't force JSON here since pollinations safely returns raw text by default
        logger.debug(f"Sending request to AI: {question}")
        raw_response = _post_json(AI_URL, {"messages": list(_mem)}, timeout=20)
        
        # Depending on network/proxy, pollinations returns either a JSON chunk or raw text.
        try:
            response_json = json.loads(raw_response)
            if isinstance(response_json, list):
                if "message" in response_json[0]:
                    full_answer = response_json[0]["message"]["content"]
                else:
                    full_answer = str(response_json[0])
            elif "choices" in response_json:
                full_answer = response_json["choices"][0]["message"]["content"]
            else:
                full_answer = response_json.get("response", response_json.get("text", str(response_json)))
        except json.JSONDecodeError:
            # It just gave us straight text, which is what we want anyway!
            full_answer = raw_response

        full_answer = _clean(full_answer.strip())
        logger.info(f"AI Response: {full_answer[:100]}...")

        # Yield chunks separated by periods
        for sentence in full_answer.split('. '):
            if sentence:
                yield sentence.strip() + "."

        _mem.append({"role": "assistant", "content": full_answer})
        
        # Save to persistent memory
        if PERSIST_MEMORY:
            try:
                save_conversation(_mem)
            except Exception as e:
                logger.error(f"Failed to save conversation: {e}")

    except socket.timeout:
        logger.warning("AI API timeout")
        yield "I couldn't reach my brain in time. Could you ask again?"
    except urlerror.URLError:
        logger.warning("No internet connection - offline fallback activated")
        yield "I'm offline right now. Could you ask me something simpler or check your internet?"
    except Exception as e:
        logger.error(f"AI fetch error: {e}")
        ui.error(f"AI Error: {e}")
        yield "Something went wrong while thinking. Please try again."


def ask(question):
    """Synchronous version"""
    sentences = list(ask_stream(question))
    return " ".join(sentences)


def forget():
    """Clear conversation memory"""
    global _mem
    _mem.clear()
    _mem.append({"role": "system", "content": AI_PROMPT})
    if PERSIST_MEMORY:
        clear_persistent_memory()
    logger.info("Memory cleared")

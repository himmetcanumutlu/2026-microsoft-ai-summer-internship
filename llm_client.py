import re
import requests
from config import LLM_MODEL, get_base_url


def strip_thinking(text):
    """Remove <think>...</think> blocks and unwanted prefixes from model output."""
    text = re.sub(r"<think>.*?</think>", "", text, flags=re.DOTALL)
    text = text.strip()
    # Remove common model hallucination prefixes
    for prefix in ["Okay,", "Ok,", "Alright,", "Let me"]:
        if text.lower().startswith(prefix.lower()):
            # Try to find the real response after the prefix
            parts = text.split(".", 1)
            if len(parts) > 1 and len(parts[1].strip()) > 10:
                text = parts[1].strip()
    return text


def build_prompt(question, sources):
    """Build chat messages from retrieved sources and the user question."""
    if not sources:
        # Simple casual chat — keep it minimal for the small model
        return [
            {"role": "user", "content": question},
        ]

    context_parts = []
    for i, src in enumerate(sources, 1):
        context_parts.append(f"[{i}] {src['filename']}:\n{src['text']}")
    context = "\n\n".join(context_parts)

    user_msg = (
        f"Answer this question using ONLY the information below.\n\n"
        f"=== DOCUMENTS ===\n{context}\n=== END DOCUMENTS ===\n\n"
        f"QUESTION: {question}\n\n"
        f"ANSWER:"
    )

    return [{"role": "user", "content": user_msg}]


def generate(messages, model=None):
    """Send chat messages to Foundry Local and return the cleaned response."""
    if model is None:
        model = LLM_MODEL

    base_url = get_base_url()
    payload = {
        "model": model,
        "messages": messages,
        "stream": False,
        "temperature": 0.1,
        "max_tokens": 300,
    }

    try:
        response = requests.post(
            f"{base_url}/chat/completions",
            json=payload,
            timeout=120,
        )
        response.raise_for_status()
        data = response.json()
        raw = data["choices"][0]["message"]["content"]
        return strip_thinking(raw)
    except requests.exceptions.ConnectionError:
        return (
            "ERROR: Could not connect to Foundry Local. "
            "Make sure it is running (`foundry server start`)."
        )
    except requests.exceptions.Timeout:
        return "ERROR: LLM response took too long. Please try again."
    except Exception as e:
        return f"ERROR: Could not get LLM response: {e}"


def answer_question(question, sources, model=None):
    """Retrieve context and generate an answer."""
    messages = build_prompt(question, sources)
    return generate(messages, model)

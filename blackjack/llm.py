"""llm.py - creates the chat model from settings in the .env file.

Copy .env.example to .env and put your API key there.
If no real key is found, get_llm() returns None and the game runs in OFFLINE mode
(simple rules instead of an LLM), so it always works.
"""
import os

try:
    from dotenv import load_dotenv
    load_dotenv()                       # read the .env file, if python-dotenv is installed
except ImportError:
    pass

# provider -> (environment variable with the API key, default cheap model)
PROVIDERS = {
    "anthropic": ("ANTHROPIC_API_KEY", "claude-haiku-5-5"),
    "openai": ("OPENAI_API_KEY", "gpt-4o-mini"),
    "google_genai": ("GOOGLE_API_KEY", "gemini-2.0-flash"),
}


def get_llm():
    """Return a LangChain chat model, or None for offline mode."""
    if os.getenv("BLACKJACK_OFFLINE") == "1":
        return None

    provider = os.getenv("LLM_PROVIDER", "anthropic").lower()
    if provider not in PROVIDERS:
        return None
    key_name, default_model = PROVIDERS[provider]
    key = os.getenv(key_name, "")
    if not key or key.startswith("your-"):       # missing, or the .env.example placeholder
        return None

    from langchain.chat_models import init_chat_model   # imported here so offline mode needs no key
    return init_chat_model(
        os.getenv("LLM_MODEL") or default_model,
        model_provider=provider,
        temperature=0.7,                         # some variety in the AI players' behaviour
        max_tokens=200,                          # answers are tiny, keeps cost low
    )

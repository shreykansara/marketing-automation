import hashlib
import re

def generate_signal_hash(title: str, url: str = "", content: str = "") -> str:
    """
    Generate SHA-256 hash using: title + url OR content snippet.
    """
    # Prefer URL if available for uniqueness
    unique_string = f"{title}|{url if url else content[:100]}"
    return hashlib.sha256(unique_string.encode('utf-8')).hexdigest()

def clean_text(text: str) -> str:
    """Basic text cleaning."""
    if not text:
        return ""
    # Strip HTML tags
    text = re.sub('<[^<]+?>', '', text)
    # Normalize whitespace
    text = re.sub(r'\s+', ' ', text).strip()
    return text

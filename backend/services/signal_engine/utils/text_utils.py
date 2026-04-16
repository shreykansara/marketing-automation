import re
import hashlib
import string

def normalize_company(name: str) -> str:
    """Lowercase and strip whitespace, removing basic corporation suffixes."""
    if not name:
        return ""
    name = name.lower().strip()
    name = re.sub(r'\b(inc|corp|ltd|llc|gmbh)\.?\b', '', name)
    return name.strip()

def extract_company(text: str) -> str | None:
    """
    Extract company name using regex heuristics like "X raises", "X secures", etc.
    """
    if not text:
        return None
        
    patterns = [
        r'([A-Z][a-zA-Z0-9&_\.-]*(?:\s[A-Z][a-zA-Z0-9&_\.-]*){0,3})\s+(?:raises|raised|secures|secured|launches|launched|announces|announced)',
        r'(?:raised|secures|secured)\s+[\$£€\d\.MmbB]+\s+(?:round|funding|seed|series)\s+for\s+([A-Z][a-zA-Z0-9&_\.-]*(?:\s[A-Z][a-zA-Z0-9&_\.-]*){0,3})'
    ]
    
    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            company_name = match.group(1).strip()
            # Simple heuristic, avoid starting with A, The heavily unless followed by capital
            if company_name.lower() in ["a", "the", "he", "she", "it", "they", "we"]:
                continue
            return company_name
            
    return None

def generate_fingerprint(company: str, normalized_text: str) -> str:
    """
    Generate fingerprint using hash(company + normalized_text[:200]).
    normalize text by lowercase, remove punctuation, trim whitespace.
    """
    if not company:
        company = ""
    if not normalized_text:
        normalized_text = ""
        
    comp = company.lower().strip()
    text = normalized_text.lower().strip()
    
    # Remove punctuation
    translator = str.maketrans('', '', string.punctuation)
    text = text.translate(translator)
    
    # Trim whitespace to single spaces
    text = re.sub(r'\s+', ' ', text)
    
    content_to_hash = comp + text[:200]
    return hashlib.sha256(content_to_hash.encode('utf-8')).hexdigest()

from typing import List

SIGNAL_WEIGHTS = {
    "funding": 40,
    "hiring_sales": 30,
    "hiring_engineering": 20,
    "product_launch": 25,
    "partnership": 15
}

def classify_text(text: str) -> List[str]:
    """
    Classify signals using keyword-based logic.
    Returns MULTIPLE signal types if applicable.
    """
    if not text:
        return []
        
    text = text.lower()
    signals = []
    
    # Funding rules
    if any(keyword in text for keyword in ["raised", "funding", "series", "seed round", "$", "million", "billion"]):
        signals.append("funding")
        
    # Hiring Sales
    if any(keyword in text for keyword in ["sales", "business development", "account executive", "go-to-market"]):
        signals.append("hiring_sales")
        
    # Hiring Engineering
    if any(keyword in text for keyword in ["engineer", "developer", "cto", "engineering team", "technical team", "architect"]):
        signals.append("hiring_engineering")
        
    # Product Launch 
    if any(keyword in text for keyword in ["launch", "released", "unveiled", "new product", "now available"]):
        signals.append("product_launch")
        
    # Partnership
    if any(keyword in text for keyword in ["partnered", "collaboration", "teamed up with", "strategic alliance", "joint venture"]):
        signals.append("partnership")
        
    return signals

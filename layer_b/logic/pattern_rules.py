def detect_patterns(text):
    text = text.lower()
    patterns = []

    if any(x in text for x in ["act now", "urgent", "immediately", "5 minutes"]):
        patterns.append("urgency")
    if any(x in text for x in ["blocked", "legal action", "police"]):
        patterns.append("fear")
    if any(x in text for x in ["bank officer", "government", "official"]):
        patterns.append("authority")

    return patterns

def split_text_by_limit(text: str, limit: int = 3500) -> list[str]:
    parts = []
    while len(text) > limit:
        split_pos = text.rfind(" ", 0, limit)
        if split_pos == -1:
            split_pos = limit
        parts.append(text[:split_pos])
        text = text[split_pos:].lstrip()
    parts.append(text)
    return parts


import html

def escape_html(text: str) -> str:
    return html.escape(text or "")

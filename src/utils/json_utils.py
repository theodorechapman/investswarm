# src/utils/json_utils.py
import json, re
from typing import Any

SMART_QUOTES = {
    "“": '"', "”": '"', "„": '"', "‟": '"',
    "’": "'", "‘": "'", "‚": "'", "‛": "'",
}

def _normalize_quotes(s: str) -> str:
    for k, v in SMART_QUOTES.items():
        s = s.replace(k, v)
    return s

def _strip_code_fences(s: str) -> str:
    # removes ```json ... ``` or ``` ... ```
    s = s.strip()
    if s.startswith("```"):
        # remove first fence
        s = re.sub(r"^```(?:json)?\s*", "", s, flags=re.IGNORECASE)
        # remove last fence
        s = re.sub(r"\s*```$", "", s)
    return s.strip()

def _first_balanced_json_object(s: str) -> str:
    start = s.find("{")
    if start < 0:
        raise ValueError("No '{' found in text")
    depth = 0
    in_str = False
    esc = False
    for i in range(start, len(s)):
        c = s[i]
        if in_str:
            if esc:
                esc = False
            elif c == "\\":
                esc = True
            elif c == '"':
                in_str = False
        else:
            if c == '"':
                in_str = True
            elif c == "{":
                depth += 1
            elif c == "}":
                depth -= 1
                if depth == 0:
                    return s[start:i+1]
    raise ValueError("Unbalanced JSON braces")

def parse_model_json(text: str) -> Any:
    s = _normalize_quotes(_strip_code_fences(text))
    try:
        chunk = _first_balanced_json_object(s)
        return json.loads(chunk)
    except Exception:
        try:
            # Optional: pip install json-repair
            from json_repair import repair_json
            repaired = repair_json(s)
            return json.loads(repaired)
        except Exception as e:
            # surface the raw text for debugging upstream
            raise ValueError(f"Failed to parse model JSON. Raw:\n{s[:5000]}") from e

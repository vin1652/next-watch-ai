import ast
import json
import re
from typing import Any, Dict, List
from groq import Groq

class GroqLLM:
    def __init__(self, api_key: str, model: str):
        self.client = Groq(api_key=api_key)
        self.model = model

    def chat(self, prompt: str, temperature: float = 0.2) -> str:
        resp = self.client.chat.completions.create(
            model=self.model,
            temperature=temperature,
            messages=[{"role": "user", "content": prompt}],
        )
        return resp.choices[0].message.content

def extract_first_json(text: str) -> Dict[str, Any]:
    if not text:
        raise ValueError("Empty model output.")

    # Prefer fenced JSON if present
    fenced = re.search(r"```(?:json)?\s*(\{.*\})\s*```", text, flags=re.DOTALL | re.IGNORECASE)
    if fenced:
        candidate = fenced.group(1)
        candidate = candidate.replace("“", "\"").replace("”", "\"").replace("’", "'")
        return json.loads(candidate)

    # Find first balanced {...}
    start = text.find("{")
    if start == -1:
        raise ValueError("No JSON object found in model output.")

    depth = 0
    in_str = False
    esc = False
    for i in range(start, len(text)):
        ch = text[i]
        if in_str:
            if esc:
                esc = False
            elif ch == "\\":
                esc = True
            elif ch == '"':
                in_str = False
        else:
            if ch == '"':
                in_str = True
            elif ch == "{":
                depth += 1
            elif ch == "}":
                depth -= 1
                if depth == 0:
                    candidate = text[start:i+1]
                    candidate = candidate.replace("“", "\"").replace("”", "\"").replace("’", "'")
                    return json.loads(candidate)

    raise ValueError("Found '{' but never found a complete balanced JSON object.")



def parse_python_list(text: str) -> List[str]:
    """
    Parse a python list from model output (handles ```python fences).
    Safe via ast.literal_eval.
    """
    s = (text or "").strip()
    s = re.sub(r"^```(?:python)?\s*", "", s)
    s = re.sub(r"\s*```$", "", s)

    m = re.search(r"\[.*\]", s, flags=re.DOTALL)
    if m:
        s = m.group(0)

    try:
        data = ast.literal_eval(s)
        if isinstance(data, list):
            return [x for x in data if isinstance(x, str)]
    except:
        return []
    return []
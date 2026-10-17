#!/usr/bin/env python3
"""Load the shared English and Korean report contracts."""
import json
from pathlib import Path
import re

STRINGS = {
    lang: json.loads((Path(__file__).resolve().parent.parent / "references" / "strings"
                      / f"{lang}.json").read_text(encoding="utf-8"))
    for lang in ("en", "ko")
}


def detect_language(text, allow_title=True):
    """Prefer an exact status line; optionally fall back to the first title."""
    lines = text.splitlines()
    for line in lines:
        for lang, strings in STRINGS.items():
            if line.strip() == strings["status_line"]:
                return lang
    if allow_title and lines and lines[0].startswith("# "):
        for lang, strings in STRINGS.items():
            if strings["title_marker"] in lines[0]:
                return lang
    return None


def label_pattern(strings, key):
    """Match a label or any alias from the contract."""
    names = [strings["labels"][key], *strings.get("label_aliases", {}).get(key, [])]
    return "(?:" + "|".join(re.escape(name) for name in names) + ")"


def template_pattern(template, replacements):
    """Escape literal text and substitute named regular expressions."""
    return "".join(replacements.get(part[1:-1], re.escape(part))
                   if part.startswith("{") and part.endswith("}") else re.escape(part)
                   for part in re.split(r"(\{[a-z_]+\})", template))


def flatten_strings(strings, prefix="s"):
    """Expose nested string leaves as dotted placeholders."""
    result = {}
    for key, value in strings.items():
        name = f"{prefix}.{key}"
        if isinstance(value, dict):
            result.update(flatten_strings(value, name))
        elif isinstance(value, str):
            result[name] = value
    return result

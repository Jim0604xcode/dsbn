from __future__ import annotations

from typing import List, Dict, Any

from .constants import (
    MASK_STYLE_FULL,
    MASK_STYLE_PARTIAL_LAST4,
    DEFAULT_MASK_CHAR,
    SPAN_PRIORITY,
    ENTITY_BANK_ACCOUNT,
    ENTITY_CREDIT_CARD,
)


def _priority(label: str) -> int:
    return SPAN_PRIORITY.get(label, 0)


def merge_spans(spans: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    # First sort by priority and length, ensuring more important/longer ones occupy first
    spans_sorted = sorted(
        spans,
        key=lambda x: (-_priority(x["label"]), -(x["end"] - x["start"]), x["start"]),
    )
    result: List[Dict[str, Any]] = []
    occupied: List[tuple[int, int]] = []
    for sp in spans_sorted:
        s, e = sp["start"], sp["end"]
        has_overlap = any(not (e <= os or s >= oe) for os, oe in occupied)
        if has_overlap:
            continue
        result.append(sp)
        occupied.append((s, e))
    # Output sorted by start point for subsequent replacement
    result.sort(key=lambda x: x["start"])
    return result


def _mask_full(original: str, mask_char: str) -> str:
    return mask_char * len(original)


def _mask_partial_last4(original: str, mask_char: str) -> str:
    n = len(original)
    keep = 4 if n >= 4 else n // 2  # Keep half when short enough
    masked_len = n - keep
    return (mask_char * masked_len) + original[-keep:]


def build_replacement(original: str, mask_style: str, mask_char: str) -> str:
    if mask_style == MASK_STYLE_PARTIAL_LAST4:
        return _mask_partial_last4(original, mask_char)
    # Default full
    return _mask_full(original, mask_char)


def apply_masks(text: str, spans: List[Dict[str, Any]], mask_style: str = MASK_STYLE_FULL, mask_char: str = DEFAULT_MASK_CHAR):
    # Requires spans to be merged and non-overlapping
    parts: list[str] = []
    last = 0
    entities: list[dict] = []
    for sp in spans:
        s, e = sp["start"], sp["end"]
        label = sp["label"]
        parts.append(text[last:s])
        original = text[s:e]
        # BANK_ACCOUNT / CREDIT_CARD use full mask
        force_full = label == ENTITY_BANK_ACCOUNT or label == ENTITY_CREDIT_CARD
        effective_style = MASK_STYLE_FULL if force_full else mask_style
        repl = build_replacement(original, effective_style, mask_char)
        parts.append(repl)
        ent = {
            "type": label,
            "text": original,
            "start": s,
            "end": e,
            "replacement": repl,
        }
        if sp.get("meta"):
            if "region" in sp["meta"] and sp["meta"]["region"]:
                ent["region"] = sp["meta"]["region"]
            if "subtype" in sp["meta"] and sp["meta"]["subtype"]:
                ent["subtype"] = sp["meta"]["subtype"]
        entities.append(ent)
        last = e
    parts.append(text[last:])
    return "".join(parts), entities



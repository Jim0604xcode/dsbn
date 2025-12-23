from __future__ import annotations
from typing import Tuple

from .schemas import MaskRequest, MaskResponse
from .detector import detect_all
from .masker import merge_spans, apply_masks


def mask_text(req: MaskRequest) -> Tuple[str, list[dict]]:
    spans = detect_all(req.text, req.locale, req.entity_types, req.phone_regions)
    merged = merge_spans(spans)
    # print(f"merged: {merged}")
    # print(f"req.text: {req.text}")
    masked_text, entities = apply_masks(
        req.text,
        merged,
        mask_style=req.mask_style,
        mask_char=req.mask_char,
    )
    return masked_text, entities


def handle_mask(req: MaskRequest) -> MaskResponse:
    masked_text, entities = mask_text(req)
    # pydantic will automatically convert the dictionary to the target model
    return MaskResponse(masked_text=masked_text, entities=entities)  # type: ignore[arg-type]



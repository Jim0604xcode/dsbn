from fastapi import APIRouter

from .schemas import MaskRequest, MaskResponse
from .service import handle_mask


router = APIRouter()


@router.post("/mask", response_model=MaskResponse)
async def mask_text_api(payload: MaskRequest) -> MaskResponse:
    return handle_mask(payload)



from fastapi import UploadFile, HTTPException
from src.loggerServices import log_error
from src.exceptions import BadReqExpection
from src.utils.fileUtil import checkFileSize
from src.constants import INVALID_IMAGE_FILE_CODE
from PIL import Image
import asyncio

async def checkImageConditions(file: UploadFile) -> None:
    """
    Check if the uploaded file meets the conditions:
    - It must be an image file.
    - It must not exceed 5MB in size.
    """
    # await checkImageFileExtension(file)
    try:
        await asyncio.gather(
            checkImageFileContent(file),
            checkImageFileExtension(file),
            checkFileSize(file),
        )
    except BadReqExpection as e:
        raise
    except Exception as e:
        raise BadReqExpection(code=INVALID_IMAGE_FILE_CODE, details="Unexpected error during image validation")
    
async def checkImageFileContent(file: UploadFile) -> None:
    """
    Verify the image content using Pillow.
    """
    try:
        image = Image.open(file.file)
        image.verify()  # Verify that it is an image
        file.file.seek(0)  # Reset file pointer after verification
    except Exception as e:
        raise BadReqExpection(code=INVALID_IMAGE_FILE_CODE, details="Invalid image file")

async def checkImageFileExtension(file: UploadFile) -> None:
    """
    Check if the file extension is allowed.
    """
    allowed_extensions = {"jpg", "jpeg", "png"}
    file_extension = file.filename.split(".")[-1].lower()
    if file_extension not in allowed_extensions:
        raise BadReqExpection(code=INVALID_IMAGE_FILE_CODE, details="Image file must be in PNG, JPG, or JPEG format")
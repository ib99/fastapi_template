from fastapi import UploadFile, File, APIRouter
import uuid
from PIL import Image
from fastapi.staticfiles import StaticFiles
router = APIRouter()

@router.post("/image/convert")
async def upload_file(image_file: UploadFile = File(...)):
    file_ext = image_file.filename.split(".")[-1]
    image = Image.open(image_file.file)
    converted_image = image.convert("RGB")
    new_file_name = f"{str(uuid.uuid4())}.webp"
    converted_image.save(f"converted_images/{new_file_name}", "WEBP")
    converted_image_url = f"http://localhost:8000/converted_images/{new_file_name}"
    return {"converted_image_url": converted_image_url}

 
router.mount("/converted_images", StaticFiles(directory="./converted_images"), name="converted_images")
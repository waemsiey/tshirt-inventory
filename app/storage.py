import os
import httpx
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.getenv("supabase_url")
SUPABASE_KEY = os.getenv("supabase_key")
SUPABASE_BUCKET = os.getenv("supabase_bucket") 

async def upload_image_to_supabase(file_name: str, file_content: bytes, content_type: str):
    file_path = f"product_images/{file_name}"

    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{SUPABASE_URL}/storage/v1/object/{SUPABASE_BUCKET}/{file_path}",
            headers={
                "apikey": SUPABASE_KEY,
                "Authorization": f"Bearer {SUPABASE_KEY}",
                "Content-Type": content_type
            },
            content=file_content
        )

    if response.status_code in [200, 201]:
        return f"{SUPABASE_URL}/storage/v1/object/public/{SUPABASE_BUCKET}/{file_path}"
    else:
        raise Exception(f"Failed to upload image: {response.text}")

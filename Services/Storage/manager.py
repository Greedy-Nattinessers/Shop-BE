import os
from uuid import uuid4

import aiofiles
import filetype
from fastapi import HTTPException


async def save_file_async(file: bytes, fid: str | None = None) -> str:
    if fid is None:
        fid = uuid4().hex

    if filetype.guess_extension(file) not in ["jpg", "png"]:
        raise HTTPException(status_code=400, detail="Invalid image type")

    async with aiofiles.open(f"Services/Storage/data/{fid}", "wb") as f:
        await f.write(file)

    return fid


async def load_file_async(fid: str) -> tuple[bytes, str] | None:
    if os.path.exists(fid):
        return None

    async with aiofiles.open(f"Services/Storage/data/{fid}", "rb") as f:
        data = await f.read()
        mime = filetype.guess_mime(data)
        if isinstance(mime, str):
            return data, mime

    return None


def remove_file(fid: str):
    if os.path.exists(f"Services/Storage/data/{fid}"):
        os.remove(f"Services/Storage/data/{fid}")

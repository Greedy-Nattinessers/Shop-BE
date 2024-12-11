import os
from pathlib import Path
from uuid import UUID, uuid4

import aiofiles
import filetype
from fastapi import HTTPException

data_path = Path(os.path.join(os.getcwd(), "Services/Storage/data"))
if not data_path.exists():
    data_path.mkdir(parents=True)


async def save_file_async(file: bytes) -> UUID:
    fid = uuid4()

    if filetype.guess_extension(file) not in ["jpg", "png"]:
        raise HTTPException(status_code=400, detail="Invalid image type")

    async with aiofiles.open(data_path.joinpath(fid.hex), "wb") as f:
        await f.write(file)

    return fid


async def load_file_async(fid: UUID) -> tuple[bytes, str] | None:
    file_path = data_path.joinpath(fid.hex)
    if not file_path.exists():
        return None

    async with aiofiles.open(file_path, "rb") as f:
        data = await f.read()
        mime = filetype.guess_mime(data)
        if isinstance(mime, str):
            return data, mime

    return None


def remove_file(fid: UUID) -> bool:
    file_path = data_path.joinpath(fid.hex)
    if file_path.exists():
        file_path.unlink()
        return True
    return False

from typing_extensions import Unpack
from pydantic import BaseModel, ConfigDict
from uuid import uuid4
#*yeah short but ... 
class cartProduct(BaseModel):
    id: str

class cartRecord(BaseModel):
    uuid: str
    cid: str
    uid: str

    def __init__(self,  cid : str, uid : str):
        super().__init__(
            uuid = uuid4().hex,
            cid = cid,
            uid = uid
        )
    



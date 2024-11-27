from typing_extensions import Unpack
from pydantic import BaseModel, ConfigDict
from uuid import uuid4
#*yeah short but ... 
class cartProduct(BaseModel):
    id: str

class cartRecord(BaseModel):
    uuid: str
    cuid: str
    uid: str

    def __init__(self,  Cuid : str, Userid : str):
        super().__init__(
            uuid = uuid4().hex,
            cuid = Cuid,
            uid = Userid
        )
    



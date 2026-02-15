from typing import Literal

from pydantic import BaseModel

from .region import Region


class GamemodePlayer(BaseModel):
    name: str
    pos: Literal[0, 1]
    region: Region
    uuid: str

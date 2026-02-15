from typing import List

from pydantic import BaseModel

from .ranking import Ranking
from .region import Region


class OverallPlayer(BaseModel):
    name: str
    points: int
    rankings: List[Ranking]
    region: Region
    uuid: str

from typing import Dict, List, Optional

from pydantic import BaseModel

from .badge import Badge
from .ranking import Ranking
from .region import Region
from .test import Test


class Player(BaseModel):
    badges: List[Badge]
    discord_id: Optional[str]
    name: str
    overall: int
    points: int
    rankings: Dict[str, Ranking]
    region: Region
    tests: List[Test]
    uuid: str

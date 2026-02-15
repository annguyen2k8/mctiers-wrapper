from typing import Literal, Optional

from pydantic import BaseModel


class Ranking(BaseModel):
    attained: int
    peak_pos: Optional[int]
    peak_tier: Literal[0, 1]
    pos: int
    retired: bool
    tier: int

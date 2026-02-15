from typing import Optional

from pydantic import BaseModel

from .test_player import TestPlayer


class Test(BaseModel):
    at: int
    gamemode: str
    player: TestPlayer
    prev_pos: Optional[int]
    prev_tier: Optional[int]
    result_pos: int
    result_tier: int
    tester: Optional[TestPlayer] = None

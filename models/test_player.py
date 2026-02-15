from typing import Optional

from pydantic import BaseModel


class TestPlayer(BaseModel):
    discord_id: Optional[str]
    name: str
    uuid: str

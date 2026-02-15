from typing import Optional

from pydantic import BaseModel


class Gamemode(BaseModel):
    discord_url: Optional[str]
    info_text: Optional[str]
    kit_image: Optional[str]
    title: str

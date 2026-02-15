from pydantic import BaseModel


class Badge(BaseModel):
    desc: str
    title: str

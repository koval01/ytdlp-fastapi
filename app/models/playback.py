from pydantic import BaseModel


class Playback(BaseModel):
    host: str
    query: str
    client_host: str

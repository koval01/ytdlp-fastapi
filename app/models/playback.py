from pydantic import BaseModel, HttpUrl, IPvAnyAddress


class Playback(BaseModel):
    url: HttpUrl
    client_host: IPvAnyAddress

from pydantic import BaseModel


class Image(BaseModel):
    url: str
    client_host: str

from pydantic import BaseModel, HttpUrl, IPvAnyAddress


class Image(BaseModel):
    url: HttpUrl
    client_host: IPvAnyAddress

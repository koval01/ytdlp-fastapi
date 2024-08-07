from pydantic import BaseModel, HttpUrl, IPvAnyAddress


class CryptoObject(BaseModel):
    url: HttpUrl
    client_host: IPvAnyAddress

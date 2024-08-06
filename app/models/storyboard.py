from pydantic import BaseModel, HttpUrl, confloat
from typing import List


class Fragment(BaseModel):
    url: HttpUrl
    duration: confloat(ge=0)


class Storyboard(BaseModel):
    fragments: List[Fragment]

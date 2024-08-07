from typing import List

from pydantic import BaseModel, HttpUrl, confloat


class Fragment(BaseModel):
    url: HttpUrl
    duration: confloat(ge=0)


class Storyboard(BaseModel):
    fragments: List[Fragment]

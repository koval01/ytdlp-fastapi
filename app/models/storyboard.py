from pydantic import BaseModel, AnyUrl, confloat
from typing import List


class Fragment(BaseModel):
    url: AnyUrl
    duration: confloat(ge=0)


class Storyboard(BaseModel):
    fragments: List[Fragment]

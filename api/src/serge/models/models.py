from typing import List

from pydantic import BaseModel


class File(BaseModel):
    name: str
    filename: str
    disk_space: float


class Model(BaseModel):
    name: str
    repo: str
    files: List[File]


class Family(BaseModel):
    name: str
    models: List[Model]


class Families(BaseModel):
    __root__: List[Family]

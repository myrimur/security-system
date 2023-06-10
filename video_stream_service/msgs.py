from pydantic import BaseModel
from typing import List

class CameraUrl(BaseModel):
    camera_id: str
    url: str

class CameraId(BaseModel):
    camera_id: str

class FrameEncodings(BaseModel):
    camera_id: str
    datetime: str
    encodings: List[List[float]]

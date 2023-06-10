from pydantic import BaseModel
from typing import List

class CameraUrl(BaseModel):
    camera_id: str
    url: str

# #https://stackoverflow.com/questions/58068001/python-pydantic-using-a-list-with-json-objects
# class CameraUrlList(BaseModel):
#     each_camera_url: List[CameraUrl]

class CameraId(BaseModel):
    camera_id: str

class FrameEncodings(BaseModel):
    camera_id: str
    datetime: str
    encodings: List[List[float]]

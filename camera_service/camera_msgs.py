from pydantic import BaseModel
from typing import List

class CameraInfo(BaseModel):
    # camera_id: str
    url: str
    location: str
    is_active: bool

class CameraUrl(BaseModel):
    camera_id: str
    url: str

#https://stackoverflow.com/questions/58068001/python-pydantic-using-a-list-with-json-objects
class CameraUrlList(BaseModel):
    each_camera_url: List[CameraUrl]

class CameraLocation(BaseModel):
    camera_id: str
    location: str

#https://stackoverflow.com/questions/58068001/python-pydantic-using-a-list-with-json-objects
class CameraLocationList(BaseModel):
    each_camera_location: List[CameraLocation]

class CameraActivity(BaseModel):
    camera_id: str
    is_active: str

class CameraId(BaseModel):
    camera_id: str
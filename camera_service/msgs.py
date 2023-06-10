from pydantic import BaseModel

class CameraInfo(BaseModel):
    camera_id: str
    url: str
    location: str
    is_active: bool

class CameraUrl(BaseModel):
    camera_id: str
    url: str

class CameraLocation(BaseModel):
    camera_id: str
    location: str

class CameraActivity(BaseModel):
    camera_id: str
    is_active: str

class CameraId(BaseModel):
    camera_id: str
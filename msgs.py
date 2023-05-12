from pydantic import BaseModel


class EncodingMsg(BaseModel):
    name: str 
    encoding: str


# TODO: borrowed from Mykhailo :+)
class Appearance(BaseModel):
    person_id: str
    camera_id: str
    location: str
    appearance_time: str

class Permission(BaseModel):
    image_path: str
    name: str
    permission: int
    camera_id: str
    
class Notification(BaseModel):
    person_id: str
    camera_id: str
    location: str
    appearance_time: str
    permission: str

class CameraInfo(BaseModel):
    camera_id: str
    location: str

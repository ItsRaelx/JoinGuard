from pydantic import BaseModel, Field, validator, constr
from typing import Optional, List

class ServerData(BaseModel):
    port: str = Field(..., pattern=r'^\d{1,5}$')
    ip: str = Field(..., pattern=r'^(\d{1,3}\.){3}\d{1,3}$')

class ReportedData(BaseModel):
    nick: str = Field(..., pattern=r'^[a-zA-Z0-9_]{3,16}$')
    ip: str = Field(..., pattern=r'^(\d{1,3}\.){3}\d{1,3}$')
    uuid: str = Field(..., pattern=r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$')

class ReportingData(BaseModel):
    nick: str = Field(..., pattern=r'^[a-zA-Z0-9_]{3,16}$')

class ReportData(BaseModel):
    server: ServerData
    reported: ReportedData
    reporting: ReportingData
    auth: str = Field(..., pattern=r'^[A-Za-z0-9-_]{30,}$')
    reason: str = Field(..., max_length=1000)

class LoginModel(BaseModel):
    _id: str

class LoginResponse(BaseModel):
    data: Optional[LoginModel] = None

class PlayerData(BaseModel):
    nick: str = Field(..., pattern=r'^[a-zA-Z0-9_]{3,16}$')
    uuid: str = Field(..., pattern=r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$')
    ip: str = Field(..., pattern=r'^(\d{1,3}\.){3}\d{1,3}$')

class LoginAttemptModel(BaseModel):
    api: str
    player: PlayerData
    server: ServerData

class ApiKeySpamModel(BaseModel):
    api_key: str = Field(..., pattern=r'^[A-Za-z0-9-_]{30,}$')

class BlacklistAddModel(BaseModel):
    nick: str = Field(..., pattern=r'^[a-zA-Z0-9_]{3,16}$')
    ip: str = Field(..., pattern=r'^(\d{1,3}\.){3}\d{1,3}$')
    uuid: str = Field(..., pattern=r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$')

class ApiResponse(BaseModel):
    status: str
    message: str

class AltsReportModel(BaseModel):
    api_key: str = Field(min_length=30, pattern=r'^[A-Za-z0-9-_]+$')
    player: PlayerData
    server: ServerData
    alts: List[constr(min_length=3, max_length=16, pattern=r'^[a-zA-Z0-9_]+$')]

class StateModel(BaseModel):
    state: str = Field(..., max_length=1024, pattern=r'^[-A-Za-z0-9+/]*={0,3}$')


class CallbackModel(BaseModel):
    code: str = Field(..., pattern=r'^[A-Za-z0-9]{30}$')
    state: str = Field(..., max_length=1024, pattern=r'^[-A-Za-z0-9+/]*={0,3}$')

class APICallbackModel(BaseModel):
    code: str = Field(..., pattern=r'^[A-Za-z0-9]{30}$')
    state: str = Field(..., pattern=r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$')
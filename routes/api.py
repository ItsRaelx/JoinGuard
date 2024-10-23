from typing import Optional

from fastapi import APIRouter
from pydantic import BaseModel

api_router = APIRouter(prefix="/api", tags=["api"])

class LoginModel(BaseModel):
    _id: str
    discord: str
    spam: bool

class LoginResponse(BaseModel):
    data: Optional[LoginModel] = None

# @api_router.get("/check", response_model=LoginResponse)
# async def read_nicks(api_key: str):
#     result = await check_api_key(api_key)
#     if result:
#         return LoginResponse(data=LoginModel(**result))
#     else:
#         raise HTTPException(status_code=401, detail="Invalid API key")

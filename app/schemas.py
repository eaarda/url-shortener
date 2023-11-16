from pydantic import BaseModel, Field, EmailStr, field_validator, HttpUrl, AfterValidator, validator, model_validator
from typing_extensions import Annotated
from datetime import datetime

from . import utils
from core.config import settings


HttpUrlString = Annotated[HttpUrl, AfterValidator(lambda v: str(v))]


class UserBase(BaseModel):
    username: str
    email: EmailStr


class UserCreate(UserBase):
    hashed_password: str = Field(..., min_length=8, max_length=30, alias="password")

    @field_validator('hashed_password')
    def validate_password(cls, hashed_password):
        try:
            return utils.is_valid_password(hashed_password)
        except ValueError as e:
            raise ValueError(str(e)) from e
        

class UserOut(UserBase):
    id: int
    created_at: datetime


class UserLogin(BaseModel):
    username: str
    password: str
        

class LinkBase(BaseModel):
    original_url: HttpUrl

    
class LinkCreate(LinkBase):
    pass


class LinkOut(LinkBase):
    id: int
    created_at: datetime
    short_id: str
    short_url: str = None
    total_clicks: int = 0

    @model_validator(mode='before')
    def autofill(cls, data):
        data.short_url = f"{settings.DOMAIN}/{data.short_id}"
        data.total_clicks = len(data.visitors)
        return data
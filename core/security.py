from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from passlib.context import CryptContext
from jwt.exceptions import InvalidTokenError, ExpiredSignatureError
import jwt, datetime
from typing import Optional
from sqlalchemy.orm import Session

from core.db import get_db
from app.crud import get_user_by_username
from core.config import settings

security = HTTPBearer(auto_error=False)


class Auth():
    ALGORITHM = "HS256"
    ACCESS_TOKEN_EXPIRES_IN = settings.ACCESS_TOKEN_EXPIRES_IN
    REFRESH_TOKEN_EXPIRES_IN = settings.REFRESH_TOKEN_EXPIRES_IN
    JWT_SECRET_KEY = settings.JWT_SECRET_KEY
    hasher = CryptContext(schemes=['bcrypt'])


    def hash_password(self, password):
        return self.hasher.hash(password)
    
    def verify_password(self, password, encoded_password):
        return self.hasher.verify(password, encoded_password)
    
    def encode_token(self, user):
        payload = {
            'exp' : datetime.datetime.utcnow() + datetime.timedelta(days=settings.ACCESS_TOKEN_EXPIRES_IN),
            'iat' : datetime.datetime.utcnow(),
            'scope' : 'access_token',
            'sub' : user.username
        }
        return jwt.encode(
            payload,
            self.JWT_SECRET_KEY,
            self.ALGORITHM
        )
    
    def decode_token(self, token):
        try:
            payload = jwt.decode(token, self.JWT_SECRET_KEY, self.ALGORITHM)
            if (payload['scope'] == 'access_token'):
                return payload
            raise HTTPException(status_code=401, detail='Scope for the token is invalid')
        except ExpiredSignatureError:
            raise HTTPException(status_code=401, detail='Token expired')
        except InvalidTokenError:
            raise HTTPException(status_code=401, detail='Invalid token')
    
    def encode_refresh_token(self, user):
        payload = {
            'exp' : datetime.datetime.utcnow() + datetime.timedelta(days=settings.REFRESH_TOKEN_EXPIRES_IN),
            'iat' : datetime.datetime.utcnow(),
            'scope': 'refresh_token',
            'sub' : user.username
        }
        return jwt.encode(
            payload, 
            self.JWT_SECRET_KEY,
            self.ALGORITHM
        )
    
    def decode_refresh_token(self, refresh_token):
        try:
            payload = jwt.decode(refresh_token, self.JWT_SECRET_KEY, self.ALGORITHM)
            if (payload['scope'] == 'refresh_token'):
                username = payload['sub']
                new_token = self.encode_token(username)
                return new_token
            raise HTTPException(status_code=401, detail='Invalid scope for token')
        except ExpiredSignatureError:
            raise HTTPException(status_code=401, detail='Refresh token expired')
        except InvalidTokenError:
            raise HTTPException(status_code=401, detail='Invalid refresh token')


def get_current_user(credentials: Optional[HTTPAuthorizationCredentials] = Depends(security), 
                     session: Session = Depends(get_db)
                     ):
    if credentials:
        token = credentials.credentials
        auth = Auth()
        try:
            payload = auth.decode_token(token)
            username = payload.get('sub')
            if username:
                user = get_user_by_username(session, username)
                if user:
                    return user
        except HTTPException as e:
            raise e
    return None
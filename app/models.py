from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, types
from sqlalchemy.orm import relationship
from datetime import datetime

from core.db import Base


class UrlType(types.TypeDecorator):
    impl = types.String

    def process_bind_param(self, value, dialect):
        if value is not None:
            return str(value)
        return None

    def process_result_value(self, value, dialect):
        if value is not None:
            return value
        return None
    

class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)

    links = relationship('Link', back_populates='user')


class Link(Base):
    __tablename__ = 'links'

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    original_url = Column(UrlType)
    short_id = Column(String(7), unique=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=True)

    user = relationship('User', back_populates='links')
    visitors = relationship('Visitor', back_populates='links')


class Visitor(Base):
    __tablename__ = 'visitors'

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    link_id = Column(Integer, ForeignKey('links.id'), nullable=False)
    ip = Column(String)
    user_agent = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)

    links = relationship('Link', back_populates='visitors')

from sqlalchemy.orm import Session

from . import schemas, models


def get_user_by_username(db: Session, username: str):
    return db.query(models.User).filter_by(username = username).first()


def create_user(db: Session, data: schemas.UserCreate):
    obj = models.User(**data.model_dump())
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


def create_link(db: Session, data: schemas.LinkCreate, short_id: str):
    obj = models.Link(**data.model_dump(), short_id=short_id)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


def get_link_by_short_id(db: Session, short_id: str):
    return db.query(models.Link).filter_by(short_id=short_id).first()


def get_user_links(db: Session, user_id: int):
    return db.query(models.Link).filter_by(user_id=user_id).all()


def create_visitor(db: Session, link_id: int, request):
    ip = request.client.host
    user_agent = request.headers.get('user-agent')

    obj = models.Visitor(
        link_id=link_id,
        ip=ip,
        user_agent=user_agent
    )
    db.add(obj)
    db.commit()
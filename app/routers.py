from fastapi import APIRouter, Depends, HTTPException, Header, Request
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from core.db import get_db
from core.security import Auth, get_current_user
from . import schemas, utils, crud


auth_handler = Auth()

router = APIRouter(
    # tags=['Shorten']
)
redirect_router = APIRouter()


@router.post('/register', summary="Create new user", response_model=schemas.UserOut, tags=['Auth'])
def register(payload: schemas.UserCreate, session: Session = Depends(get_db)):
    existing_user = crud.get_user_by_username(session, payload.username)
    if existing_user:
        raise HTTPException(status_code=400, detail="User already exists")
        
    payload.hashed_password = auth_handler.hash_password(payload.hashed_password)
    created_user = crud.create_user(session, payload)
    return created_user


@router.post('/login', summary="Login", tags=['Auth'])
def login(payload: schemas.UserLogin, session: Session = Depends(get_db)):
    db_user = crud.get_user_by_username(session, payload.username)
    if not db_user or not auth_handler.verify_password(payload.password, db_user.hashed_password):
        raise HTTPException(status_code=400, detail="Invalid credentials")
    
    access_token = auth_handler.encode_token(db_user)
    refresh_token = auth_handler.encode_refresh_token(db_user)

    return {"access_token": access_token, "refresh_token": refresh_token}


@router.post('/shorten', tags=['Shorten'], response_model=schemas.LinkOut)
def create_short_url(payload: schemas.LinkCreate,
                     session: Session = Depends(get_db),
                     current_user: dict = Depends(get_current_user)):
    
    short_id = utils.create_short_id(payload.original_url)
    short_link = crud.create_link(session, payload, short_id)

    if current_user:
        short_link.user = current_user
        session.commit()
    
    return short_link


@router.get('/links', tags=['Users'], response_model=list[schemas.LinkOut])
def get_user_links(session: Session = Depends(get_db), 
                   current_user: dict = Depends(get_current_user)):
    if not current_user:
        raise utils.not_authenticated()
    # db_links = current_user.links
    db_links = crud.get_user_links(session, current_user.id)
    return db_links


@redirect_router.get("/{short_id}", tags=['Shorten'])
def redirect_original_url(short_id: str, 
                          request: Request,
                          session: Session = Depends(get_db)):
    db_link = crud.get_link_by_short_id(session, short_id)
    if not db_link:
        raise HTTPException(status_code=404, detail="Not found")
    crud.create_visitor(session, db_link.id, request)
    return RedirectResponse(url=db_link.original_url)
from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security.oauth2 import OAuth2AuthorizationCodeBearer

from sqlalchemy.orm import Session

from common import auth
from app.database import get_db
from app.schemas import UserBase
from app.models import User
from common import logger

router = APIRouter(prefix='/auth', tags=["AUTH"])

oauth2_scheme = OAuth2AuthorizationCodeBearer(authorizationUrl="auth/swagger",tokenUrl='auth/swagger') # type: ignore

@router.post('/sign')
async def sign_up(data:UserBase, db:Session= Depends(get_db)):
    name_exist = db.query(User).filter(User.name==data.name).first()
    logger.debug(name_exist)
    if name_exist:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f'{data.name} already exist'
        )
    
    new_user = User(
        name = data.name
    )
    
    db.add(new_user)
    db.commit()
    
    tokens = auth.create_tokens(subject=new_user.name)
    
    return tokens


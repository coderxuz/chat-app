from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security.oauth2 import OAuth2AuthorizationCodeBearer

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from common import auth
from app.database import get_async_db
from app.schemas import UserBase
from app.models import User
from common import logger

router = APIRouter(prefix='/auth', tags=["AUTH"])

oauth2_scheme = OAuth2AuthorizationCodeBearer(authorizationUrl="auth/swagger",tokenUrl='auth/swagger') # type: ignore

@router.post('/sign')
async def sign_up(data:UserBase, db:AsyncSession= Depends(get_async_db)):
    name_query = await db.execute(select(User).where(User.name == data.name))
    name_exist = name_query.scalars().first()
    
    logger.debug(name_exist)
    if name_exist:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f'{data.name} already exist'
        )
    
    new_user = User(
        name = data.name,
        password=auth.hash_password(password=data.password)
    )
    
    db.add(new_user)
    await db.commit()
    
    tokens = auth.create_tokens(subject=new_user.name)
    
    return tokens


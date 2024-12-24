from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security.oauth2 import OAuth2PasswordBearer, OAuth2PasswordRequestForm

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from common import auth
from app.database import get_async_db
from app.schemas import UserBase, TokensResponse, TokensResponseSwagger
from app.models import User
from common import logger

router = APIRouter(prefix='/auth', tags=["AUTH"])

oauth2_scheme = OAuth2PasswordBearer(tokenUrl='auth/swagger') 

@router.post('/sign', response_model=TokensResponse)
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

@router.post('/login', response_model=TokensResponse)
async def login(data:UserBase, db:AsyncSession=Depends(get_async_db)):
    
    user_query = await db.execute(select(User).where(User.name == data.name))
    db_user = user_query.scalars().first()
    
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"{data.name} not found whit this credentials"
        )
    
    if not auth.verify_password(data.password, db_user.password):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"{data.name} not found whit this credentials"
        )
    
    return auth.create_tokens(subject=db_user.name)

@router.post('/swagger', response_model=TokensResponseSwagger)
async def swagger(data:OAuth2PasswordRequestForm = Depends(), db:AsyncSession=Depends(get_async_db)):
    
    user_query = await db.execute(select(User).where(User.name == data.username))
    db_user = user_query.scalars().first()
    
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"{data.username} not found whit this credentials"
        )
    
    if not auth.verify_password(data.password, db_user.password):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"{data.username} not found whit this credentials"
        )
    tokens = auth.create_tokens(subject=db_user.name)
    return {"access_token":tokens.get('accessToken'), "refresh_token":tokens['refreshToken']}
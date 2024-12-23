from fastapi import APIRouter, Depends,  WebSocket, WebSocketDisconnect, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from pydantic import ValidationError

# from common import auth
from app.database import get_async_db
from app.models import User, Chat
from app.connection import ConnectionManager
from common import logger
from app.funcs.token import get_token
from app.schemas import MessageData

from typing import Optional

router = APIRouter(prefix='/chat', tags=["CHAT"])


manager = ConnectionManager()


@router.websocket("/ws")
async def websocket_end(websocket: WebSocket, db:AsyncSession = Depends(get_async_db)):
    db_user = None
    try:
        subject  = await get_token(websocket=websocket)
        if not subject:
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
            return
        
        db_user_query = await db.execute(select(User).where(User.name == subject))
        db_user = db_user_query.scalars().first()
        if not db_user:
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
            return
        
        user_name = websocket.query_params.get("user_name")
        if not user_name:
            await websocket.send_json({"message": "user_name"})
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
            return
        receivers_socket:Optional[WebSocket] = None
        receiver_query = await db.execute(select(User).where(User.name == user_name))
        receiver = receiver_query.scalars().first()
        
            
            
        if  not receiver:
            logger.debug('receiver not found from db')
            await websocket.send_json({"message": "receiver not found"})
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
            return
        receivers_socket = await manager.get_receivers_socket(user_name)
            
        await manager.connect(user_name=db_user.name, websocket=websocket)
        if receivers_socket is None:
                logger.debug('receiver not found')
                await websocket.send_json({"message":f"{user_name} not online"})
        
        while True:
            if user_name:  
                receivers_socket = await manager.get_receivers_socket(user_name)
            data = await websocket.receive_json()
            logger.debug(manager.active_connections)
            try:
                message_json=MessageData(**data)
                logger.debug(type(receivers_socket))
                
                new_message = Chat(
                    message= message_json.message,
                    sender_id= db_user.id,
                    receiver_id = receiver.id
                )
                db.add(new_message)
                await db.commit()
                await db.refresh(new_message)
                if receivers_socket:
                    await receivers_socket.send_json(data=data)
                else:
                    await websocket.send_json({"message": "receiver not connected"})
            except ValidationError:
                await websocket.send_json({"message":"please send valid data (message didn't send)"})
            
            
    except WebSocketDisconnect:
        if db_user:
            manager.disconnect(user_name=db_user.name)
    except HTTPException as e:
        if db_user:
            manager.disconnect(user_name=db_user.name)
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
    except Exception as e:
        if db_user:
            manager.disconnect(user_name=db_user.name)
        logger.error(f"Unexpected error: {e}")
        logger.error(f"Unexpected error: {e.__dict__}")
        await websocket.close(code=status.WS_1011_INTERNAL_ERROR)

from fastapi import APIRouter, Depends,  WebSocket, WebSocketDisconnect, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from pydantic import ValidationError

# from common import auth
from app.database import get_async_db
from app.models import User
from app.connection import manager
from common import logger
from app.funcs.token import get_token
from app.schemas import MessageData
from app.funcs.chat_funcs import query_get_receivers_socket, ReceiverNotFound, add_new_chat_to_db

import json

router = APIRouter(prefix='/chat', tags=["CHAT"])





@router.websocket("/ws")
async def websocket_end(websocket: WebSocket, db:AsyncSession = Depends(get_async_db)):
    db_user = None
    try:
        #getting current user from database
        subject  = await get_token(websocket=websocket)
        if not subject:
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
            return
        
        db_user_query = await db.execute(select(User).where(User.name == subject))
        db_user = db_user_query.scalars().first()
        if not db_user:
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
            return
        
        #accepting socket and adding to self.active connections
        await manager.connect(db_user.name, websocket=websocket)
        
        while True: 
            # getting receiver
            receivers_data = await query_get_receivers_socket(current_socket=websocket, db_user=db_user, db=db)
            
            receivers_socket = receivers_data.get('receivers_socket')
            receiver = receivers_data.get('receiver')
            
            if not receiver:
                raise ReceiverNotFound
            
            #message
            data = await websocket.receive_json()
            logger.debug(manager.active_connections)
            if not data:
                await websocket.send_json({"message": "Empty message received"})
                continue
            try:
                message_json = MessageData(**data)
                logger.debug(type(receivers_socket))
                
                #adding to db
                await add_new_chat_to_db(message=message_json.message, sender_id=db_user.id, receiver_id=receiver.id, db=db)
                
                if receivers_socket:
                    await receivers_socket.send_json(data=data)
                else:
                    await websocket.send_json({"message": "receiver not connected"})
            except (ValidationError, json.JSONDecodeError)as e:
                await websocket.send_json({"message": "please send valid data (message didn't send)"})
                logger.error(f"Validation error: {e}")
            
            
    except WebSocketDisconnect:
        if db_user:
            manager.disconnect(user_name=db_user.name)
    except HTTPException as e:
        if db_user:
            manager.disconnect(user_name=db_user.name)
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
    except ReceiverNotFound:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
    except Exception as e:
        if db_user:
            manager.disconnect(user_name=db_user.name)
        logger.error(f"Unexpected error: {e}")
        await websocket.close(code=status.WS_1011_INTERNAL_ERROR)

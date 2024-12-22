from fastapi import APIRouter, Depends,  WebSocket, WebSocketDisconnect, status
from sqlalchemy.orm import Session

from common import auth
from app.database import get_db
from app.models import User
from app.connection import ConnectionManager
from common import logger


router = APIRouter(prefix='/chat', tags=["CHAT"])

manager = ConnectionManager()


@router.websocket("/ws")
async def websocket_end(websocket: WebSocket, db:Session = Depends(get_db)):
    db_user = None
    try:
        token = websocket.headers.get('token')
        logger.debug(token)
        if not token:
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
            return
        subject = auth.get_subject(token=token)
    
        db_user = db.query(User).filter(User.name == subject).first()
    
        if not db_user:
            raise WebSocketDisconnect
        await manager.connect(user_name=db_user.name, websocket=websocket)
        
        while True:
            data = await websocket.receive_json()
            await websocket.send_json(data=data)
    except WebSocketDisconnect:
        if db_user:
            manager.disconnect(user_name=db_user.name)
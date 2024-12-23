from fastapi import WebSocket, status

from common import auth, logger


async def get_token(websocket: WebSocket):
    token = websocket.query_params.get("token")
    logger.debug(token)
    
    if not token:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return
    
    subject = auth.get_subject(token=token)
    return subject

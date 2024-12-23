from fastapi import WebSocket

from typing import Dict, Optional

from common import logger


class ConnectionManager:
    """Class defining socket events"""

    def __init__(self) -> None:
        """init method, keeping track of connections"""
        self.active_connections: Dict[str, WebSocket] = {}

    async def connect(self, user_name: str, websocket: WebSocket) -> None:
        """connect event"""
        logger.debug(f"Connect called user_name:{user_name}")
        await websocket.accept()
        self.active_connections[user_name] = websocket

    async def send_personal_message(self, message: str, websocket: WebSocket) -> None:
        """Direct Message"""
        await websocket.send_text(message)
    
    async def get_receivers_socket(self,user_name:str)->Optional[WebSocket]:
        logger.debug(f"get_socket user_name:{user_name}")
        receivers_socket = self.active_connections.get(user_name)
        logger.debug(receivers_socket)
        logger.debug(self.active_connections)
        if not receivers_socket:
            return None
        return receivers_socket
    
    def disconnect(self, user_name: str) -> None:
        """disconnect event"""
        logger.debug(f"Called to disconnect user_name{user_name}")
        self.active_connections.pop(user_name, None)

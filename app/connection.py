from fastapi import WebSocket

from typing import Dict


class ConnectionManager:
    """Class defining socket events"""

    def __init__(self) -> None:
        """init method, keeping track of connections"""
        self.active_connections: Dict[str, WebSocket] = {}

    async def connect(self, user_name: str, websocket: WebSocket) -> None:
        """connect event"""
        await websocket.accept()
        self.active_connections[user_name] = websocket

    async def send_personal_message(self, message: str, websocket: WebSocket) -> None:
        """Direct Message"""
        await websocket.send_text(message)

    def disconnect(self, user_name: str) -> None:
        """disconnect event"""
        self.active_connections.pop(user_name)

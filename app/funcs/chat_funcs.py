from fastapi import WebSocket, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.database import get_async_db
from app.models import User, Chat
from common import logger
from app.connection import manager

from typing import Optional, TypedDict


class ReceiversDict(TypedDict):
    receivers_socket: Optional[WebSocket]
    receiver: User

#custom exception
class ReceiverNotFound(Exception):
    pass


async def query_get_receivers_socket(
    current_socket: WebSocket, db_user: User, db: AsyncSession = Depends(get_async_db)
) -> ReceiversDict:

    user_name = current_socket.query_params.get("user_name")
    if not user_name:
        await current_socket.send_json({"message": "user_name not found"})
        raise ReceiverNotFound
    receivers_socket: Optional[WebSocket] = None
    receiver_query = await db.execute(select(User).where(User.name == user_name))
    receiver = receiver_query.scalars().first()

    if receiver is None:
        logger.debug("receiver not found from db")
        await current_socket.send_json({"message": "receiver not found"})
        raise ReceiverNotFound

    receivers_socket = await manager.get_receivers_socket(user_name)

    if receivers_socket is None:
        logger.debug("receiver not found")
        await current_socket.send_json({"message": f"{user_name} not online"})
    return {"receivers_socket": receivers_socket, "receiver": receiver}


async def add_new_chat_to_db(
    sender_id: int,
    receiver_id: int,
    message: str,
    db: AsyncSession = Depends(get_async_db),
) -> None:
    new_message = Chat(message=message, sender_id=sender_id, receiver_id=receiver_id)
    db.add(new_message)
    await db.commit()
    await db.refresh(new_message)

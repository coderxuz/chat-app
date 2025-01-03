from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship, Mapped, mapped_column

from app.database import Base, engine


class User(Base):
    __tablename__ = "users"

    name: Mapped[str] = mapped_column(unique=True)
    password:Mapped[str]

    sent_messages: Mapped["Chat"] = relationship(
        back_populates="sender", foreign_keys="[Chat.sender_id]"
    )
    received_messages: Mapped["Chat"] = relationship(
        back_populates="receiver", foreign_keys="[Chat.receiver_id]"
    )


class Chat(Base):
    __tablename__ = "chats"

    message: Mapped[str]
    sender_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    receiver_id: Mapped[int] = mapped_column(ForeignKey("users.id"))

    sender: Mapped["User"] = relationship(
        back_populates="sent_messages", foreign_keys=[sender_id]
    )
    receiver: Mapped["User"] = relationship(
        back_populates="received_messages", foreign_keys=[receiver_id]
    )
    def __init__(self,sender_id:int, receiver_id:int, message:str):
        self.receiver_id = receiver_id
        self.sender_id = sender_id
        self.message = message


if __name__ == '__main__':
    Base.metadata.create_all(engine)
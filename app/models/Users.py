from sqlalchemy import Column, Enum, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from db.session import Base
from schemas.Users import UserStatus


class Users(Base):
    __tablename__ = "users"
    __table_args__ = {'sqlite_autoincrement': True}

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(255))
    email = Column(String(255), unique=True, index=True)
    status = Column(Enum(UserStatus), default=UserStatus.enabled)
    hashed_password = Column(String(255))

    permission_id = Column(Integer, ForeignKey("permissions.id"))
    permission = relationship("Permissions", back_populates="user")

    def __repr__(self):
        return f"<User ({self.id}) name={self.name} - email={self.email}>"

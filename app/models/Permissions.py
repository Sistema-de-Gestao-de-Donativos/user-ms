from sqlalchemy import Column, Integer, Enum
from sqlalchemy.orm import relationship

from db.session import Base
from schemas.Permissions import UserRole
# Required for the relationship between Permissions and Users
import models.Users


class Permissions(Base):
    __tablename__ = "permissions"
    __table_args__ = {'sqlite_autoincrement': True}

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    max_concurrent_gpus = Column(Integer)
    type = Column(Enum(UserRole), default=UserRole.developer)

    user = relationship("Users", back_populates="permission")

    def __repr__(self):
        return f"<Permissions ({self.id}) max_concurrent_gpus={self.max_concurrent_gpus} - userType={self.type}>"

from sqlalchemy import Column, Integer, String

from db.session import Base


class AccessLogs(Base):
    __tablename__ = "access_logs"
    __table_args__ = {'sqlite_autoincrement': True}

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    token = Column(String(510))

    def __repr__(self):
        return f"<AccessLogs(id={self.id}, token={self.token})>"

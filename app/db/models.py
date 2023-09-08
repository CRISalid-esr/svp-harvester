from sqlalchemy import Boolean, Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from app.db.session import Base


class Retrieval(Base):
    __tablename__ = "retrievals"

    id = Column(Integer, primary_key=True, index=True)
    

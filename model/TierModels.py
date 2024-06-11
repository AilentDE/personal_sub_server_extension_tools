from sqlalchemy import Column, String, Integer, DateTime, Boolean, Date, NVARCHAR
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Tier(Base):
    __tablename__ = "Tier"

    creatorID = Column(String(255), primary_key=True, nullable=False)
    tierID = Column(String(225), primary_key=True, nullable=False)
    tierName = Column(NVARCHAR(255))
    depiction = Column(NVARCHAR)
    price = Column(Integer)
    limit = Column(Integer)
    bannerID = Column(String(255))
    openDate = Column(DateTime)
    isListed = Column(Boolean)
    isRestricted = Column(Boolean)
    isAddon = Column(Boolean)
    createdAt = Column(DateTime)
    updatedAt = Column(DateTime)
    destroyedAt = Column(DateTime)
    renewAt = Column(Date)
    expiredAt = Column(Date)
    IsDelete = Column(Boolean)
    CanDelete = Column(Boolean)
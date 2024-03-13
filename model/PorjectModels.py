from sqlalchemy import Column, Integer, String, DateTime, Boolean
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Project(Base):
    __tablename__ = "Activity"

    activityID = Column(String(225), primary_key=True)
    userID = Column(String(225))
    title = Column(String(100))
    depiction = Column(String)
    imageUrl = Column(String)
    startDate = Column(DateTime)
    endDate = Column(DateTime)
    activityPlace = Column(String(200))
    browseCount = Column(Integer)
    createTime = Column(DateTime)
    updateTime = Column(DateTime)
    isPublic = Column(Boolean)
    isDelete = Column(Boolean)
    isRecommended = Column(Integer)
    deleteTime = Column(DateTime)
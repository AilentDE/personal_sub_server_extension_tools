from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Work(Base):
    __tablename__ = "Work"

    workID = Column(String(225), primary_key=True, nullable=False)
    title = Column(Text, nullable=True)
    depiction = Column(Text, nullable=True)
    userID = Column(String(225), nullable=True)
    workType = Column(String(225), nullable=True)
    bannerID = Column(Text, nullable=True)
    bannerModel = Column(String(20), nullable=True)
    externalMediaURL = Column(Text, nullable=True)
    publicSetting = Column(String(20), nullable=True)
    IsPublish = Column(Boolean, nullable=True)
    activityID = Column(String(225), nullable=True)
    browseCount = Column(Integer, nullable=True)
    publishTime = Column(DateTime, nullable=True)
    bodyHtml = Column(Text, nullable=True)
    typeID = Column(String(225), nullable=True)
    isNSFW = Column(Boolean, nullable=True)
    isPinned = Column(Boolean, nullable=True)
    createTime = Column(DateTime, nullable=True)
    updateTime = Column(DateTime, nullable=True)
    isDelete = Column(Boolean, default=False, nullable=True)
    deleteTime = Column(DateTime, nullable=True)
    isRecommended = Column(Boolean, nullable=True)

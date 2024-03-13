from sqlalchemy import Column, String, Boolean, Integer, DateTime
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class UserSubscription(Base):
    __tablename__ = "UserSubscription"
    userID = Column(String(255), primary_key=True)
    creatorID = Column(String(255), primary_key=True)
    tierID = Column(String(255), primary_key=True)
    subscription_Year = Column(String(4), primary_key=True)
    subscription_Month = Column(String(2), primary_key=True)
    createTime = Column(DateTime)
    updateTime = Column(DateTime)
    price = Column(Integer)
    IsPay = Column(Boolean)
    isAddon = Column(Boolean)
    cancelTime = Column(DateTime)
    cancelUser = Column(String(255))
    isRenew = Column(Boolean)

class UserSubscriptionPurview(Base):
    __tablename__ = "UserSubscriptionPurview"
    userID = Column(String(255), primary_key=True)
    creatorID = Column(String(255), primary_key=True)
    tierID = Column(String(255), primary_key=True)
    subscription_Year = Column(String(4), primary_key=True)
    subscription_Month = Column(String(2), primary_key=True)
    createTime = Column(DateTime)
    price = Column(Integer)
    isAddon = Column(Boolean)
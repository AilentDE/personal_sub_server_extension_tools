from sqlalchemy import Column, String, Boolean, Integer, DateTime
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Order(Base):
    __tablename__ = 'Order'

    orderID = Column(String(255), primary_key=True)  # 主鍵
    createTime = Column(DateTime)
    orderType = Column(String(30))
    orderStatus = Column(String(30))
    userID = Column(String(255))
    creatorID = Column(String(255))
    totalPrice = Column(Integer)
    memo = Column(String)
    cashFee = Column(Integer)
    orderFee = Column(Integer)
    platformFee = Column(Integer)
    isCheckout = Column(Boolean)

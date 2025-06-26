from sqlalchemy import (
    Column,
    Integer,
    SmallInteger,
    String,
    DateTime,
    Date,
    Boolean,
    Text,
    ForeignKey,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


class UserData(Base):
    __tablename__ = "UserData"

    userID = Column(String(255), primary_key=True, nullable=False)
    displayName = Column(String(255), nullable=True)
    tel = Column(String(20), nullable=True)
    email = Column(String(255), nullable=True)
    birthday = Column(Date, nullable=True)
    password = Column(String(255), nullable=True)
    externalUrl = Column(String, nullable=True)
    showNSFW = Column(Boolean, nullable=True)
    locale = Column(String, nullable=True)
    createdAt = Column(DateTime, nullable=True)
    lastSignedInAt = Column(DateTime, nullable=True)
    avatarAssetID = Column(String(225), nullable=True)
    creatorBannerAssetID = Column(String(225), nullable=True)
    isWork = Column(Boolean, nullable=True)
    isAdmin = Column(Boolean, nullable=True)
    UTC = Column(SmallInteger, nullable=True)
    isRecommended = Column(Boolean, nullable=True)
    platformFeePercent = Column(SmallInteger, nullable=True)
    creditToken = Column(String(255), nullable=True)
    balance = Column(Integer, nullable=True)
    isDisable = Column(Boolean, nullable=True)
    creditNo = Column(String(4), nullable=True)
    updateTime = Column(DateTime, nullable=True)


class CreatorType(Base):
    __tablename__ = "CreatorType"

    creatorID = Column(String(255), primary_key=True, nullable=False)
    typeID = Column(String(15), primary_key=True, nullable=False)
    updateTime = Column(DateTime, nullable=True)
    sort = Column(Integer, nullable=True)


class UserCashRecord(Base):
    __tablename__ = "UserCashRecord"
    rowID = Column(String(255), primary_key=True, nullable=False)
    userID = Column(String(255), ForeignKey("UserRealData.userID"), nullable=False)
    cashType = Column(String(50), nullable=True)
    orderFee = Column(Integer, nullable=True)
    platformFee = Column(Integer, nullable=True)
    cashFee = Column(Integer, nullable=True)
    netProfit = Column(Integer, nullable=True)
    status = Column(String(30), nullable=True)
    createTime = Column(DateTime, nullable=True)
    updateTime = Column(DateTime, nullable=True)
    isDelete = Column(Boolean, nullable=True)
    memo = Column(Text, nullable=True)

    user_real_data = relationship("UserRealData", back_populates="cash_records")


class UserRealData(Base):
    __tablename__ = "UserRealData"
    userID = Column(String(255), primary_key=True, nullable=False)
    userRealName = Column(String(10), nullable=True)
    bankName = Column(String(50), nullable=True)
    bankBranchName = Column(String(200), nullable=True)
    bankNo = Column(String(10), nullable=True)
    bankAccount = Column(String(20), nullable=True)
    balance = Column(Integer, nullable=True)
    nextRemitTime = Column(DateTime, nullable=True)
    accountCertified = Column(String(30), nullable=True)
    bankImageID = Column(String(255), nullable=True)
    identityCardFrontID = Column(String(255), nullable=True)
    identityCardBackID = Column(String(255), nullable=True)
    reason = Column(Text, nullable=True)
    identityNumber = Column(String(20), nullable=True)
    createTime = Column(DateTime, nullable=True)
    updateTime = Column(DateTime, nullable=True)
    swiftCode = Column(String(11), nullable=True)
    identityType = Column(String(20), nullable=True)
    passportAssetId = Column(String(255), nullable=True)
    identityDocumentAssetId = Column(String(255), nullable=True)
    identityDocument2AssetId = Column(String(255), nullable=True)

    cash_records = relationship("UserCashRecord", back_populates="user_real_data")

from fastapi import APIRouter, Query, Path, Depends, HTTPException, status
from fastapi.responses import FileResponse
from typing import Annotated
from sqlalchemy import select, func, delete, insert
from sqlalchemy.orm import Session, aliased
from model.UserModels import UserData, CreatorType
from model.SubscriptionModels import UserSubscription
from model.TierModels import Tier
from config.database import engine, get_db
import pandas as pd
from datetime import datetime, timedelta, timezone
from dateutil.relativedelta import relativedelta
import tempfile
from collections import namedtuple

router = APIRouter(
    prefix='/user',
    tags=['Users']
)

@router.get("/userData")
async def get_user_data(
    creator_types: list[str]= Query(default=['illustration', 'comic', 'cosplay', 'sound', 'game', 'model', 'other', 'none'],
                                   description='options of illustration, comic, cosplay, sound, game, model, other or **none** .'),
    created_from: datetime|None = Query(default=None,
                                        description='YYYY-MM-DDTHH:mm:ssZ \(UTC+0\)'),
    created_until: datetime|None = Query(default=None,
                                         description='YYYY-MM-DDTHH:mm:ssZ \(UTC+0\)')):
    print(creator_types)
    stmt = select(
        UserData.userID,
        UserData.displayName,
        UserData.email,
        UserData.createdAt,
        func.aggregate_strings(CreatorType.typeID, ',').label('creatorFields')
    ).join(CreatorType, UserData.userID == CreatorType.creatorID, isouter=True)
    if 'none' not in creator_types:
        stmt = stmt.where(CreatorType.typeID.in_(creator_types))
    elif creator_types == ['none']:
        stmt = stmt.where(CreatorType.typeID==None)
    if created_from:
        stmt = stmt.where(UserData.createdAt > created_from)
    if created_until:
        stmt = stmt.where(UserData.createdAt <= created_until)
    stmt = stmt.group_by(UserData.userID, UserData.displayName, UserData.email, UserData.createdAt).order_by(UserData.createdAt.asc())
    # data
    with engine.connect() as conn:
        data = pd.read_sql_query(stmt, conn)
        def check_creator_type(types_string:str|None, type:str):
            if types_string is None:
                return 0
            elif type in types_string:
                return 1
            else:
                return 0
        data['createdAt'] = data['createdAt'].apply(lambda x: x+timedelta(hours=8))
        data['illustration'] = data['creatorFields'].apply(lambda x: check_creator_type(x, 'illustration'))
        data['comic'] = data['creatorFields'].apply(lambda x: check_creator_type(x, 'comic'))
        data['cosplay'] = data['creatorFields'].apply(lambda x: check_creator_type(x, 'cosplay'))
        data['sound'] = data['creatorFields'].apply(lambda x: check_creator_type(x, 'sound'))
        data['game'] = data['creatorFields'].apply(lambda x: check_creator_type(x, 'game'))
        data['model'] = data['creatorFields'].apply(lambda x: check_creator_type(x, 'model'))
        data['other'] = data['creatorFields'].apply(lambda x: check_creator_type(x, 'other'))
        # excel
        with tempfile.NamedTemporaryFile(delete=False, suffix='.xlsx') as temp_file:
            data.to_excel(temp_file.name, index=False)
    return FileResponse(path=temp_file.name, filename=f'user_list_{datetime.now().strftime("%Y%m%d%H%M%S")}.xlsx', media_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')

@router.get("/subscribe/now")
async def show_user_subscribe(db: Annotated[Session, Depends(get_db)],
                              user_id: list[str] = Query(default=['none'], description='none for not specify.'),
                              creator_id: list[str] = Query(default=['none'], description='none for not specify.')):
    # if user_id is None and creator_id is None:
    #     raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE, detail=' not allow both user and creator to be empty data.')
    user1 = aliased(UserData)
    user2 = aliased(UserData)
    stmt = select(
        UserSubscription.userID,
        user1.displayName.label('userName'),
        user1.email.label('userEmail'),
        UserSubscription.subscription_Year,
        UserSubscription.subscription_Month,
        UserSubscription.tierID,
        UserSubscription.price,
        UserSubscription.creatorID,
        user2.displayName.label('creatorName'),
        user2.email.label('creatorEmail'),
    ).join(
        user1, UserSubscription.userID == user1.userID
    ).join(
        user2, UserSubscription.creatorID == user2.userID
    ).where(
        UserSubscription.subscription_Year == (datetime.now(timezone.utc)+timedelta(hours=8)).strftime('%Y'),
        UserSubscription.subscription_Month == (datetime.now(timezone.utc)+timedelta(hours=8)).strftime('%m'),
        UserSubscription.IsPay == 1
    )
    if user_id and user_id != ['none']:
        stmt = stmt.where(
            UserSubscription.userID.in_(user_id)
        )
    if creator_id and creator_id != ['none']:
        stmt = stmt.where(
            UserSubscription.creatorID.in_(creator_id)
        )
    with engine.connect() as conn:
        data = pd.read_sql_query(stmt, conn)
        with tempfile.NamedTemporaryFile(delete=False, suffix='.xlsx') as temp_file:
            data.to_excel(temp_file.name, index=False)
    return FileResponse(path=temp_file.name, filename=f'user_subscribe_creator_{datetime.now().strftime("%Y%m%d%H%M%S")}.xlsx', media_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')

@router.get("/subscribe/next")
async def show_user_subscribe(db: Annotated[Session, Depends(get_db)],
                              user_id: list[str] = Query(default=['none'], description='none for not specify.'),
                              creator_id: list[str] = Query(default=['none'], description='none for not specify.')):
    # if user_id is None and creator_id is None:
    #     raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE, detail=' not allow both user and creator to be empty data.')
    user1 = aliased(UserData)
    user2 = aliased(UserData)
    stmt = select(
        UserSubscription.userID,
        user1.displayName.label('userName'),
        user1.email.label('userEmail'),
        UserSubscription.subscription_Year,
        UserSubscription.subscription_Month,
        UserSubscription.tierID,
        UserSubscription.price,
        UserSubscription.creatorID,
        user2.displayName.label('creatorName'),
        user2.email.label('creatorEmail'),
    ).join(
        user1, UserSubscription.userID == user1.userID
    ).join(
        user2, UserSubscription.creatorID == user2.userID
    ).where(
        UserSubscription.subscription_Year == (datetime.now(timezone.utc)+timedelta(hours=8)+relativedelta(months=1)).strftime('%Y'),
        UserSubscription.subscription_Month == (datetime.now(timezone.utc)+timedelta(hours=8)+relativedelta(months=1)).strftime('%m'),
    )
    if user_id and user_id != ['none']:
        stmt = stmt.where(
            UserSubscription.userID.in_(user_id)
        )
    if creator_id and creator_id != ['none']:
        stmt = stmt.where(
            UserSubscription.creatorID.in_(creator_id)
        )
    with engine.connect() as conn:
        data = pd.read_sql_query(stmt, conn)
        with tempfile.NamedTemporaryFile(delete=False, suffix='.xlsx') as temp_file:
            data.to_excel(temp_file.name, index=False)
    return FileResponse(path=temp_file.name, filename=f'user_subscribe_creator_{datetime.now().strftime("%Y%m%d%H%M%S")}.xlsx', media_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')

@router.delete("/subscribe/next")
async def cancel_user_subscribe(db: Annotated[Session, Depends(get_db)],
                                user_id: str = Query(description='欲退訂的使用者ID'),
                                tier_id: str = Query(description='欲退訂的方案ID')):
    now_datetime = datetime.now(timezone.utc)+timedelta(hours=8)
    date_data = namedtuple("DateData", ["this_year", "this_month", "next_year", "next_month"])(
        now_datetime.strftime('%Y'),
        now_datetime.strftime('%m'),
        (now_datetime+relativedelta(months=1)).strftime('%Y'),
        (now_datetime+relativedelta(months=1)).strftime('%m'),
    )
    print(user_id, tier_id, date_data)
    stmt = select(
        UserSubscription
    ).where(
        UserSubscription.userID == user_id,
        UserSubscription.tierID == tier_id,
        UserSubscription.subscription_Year == date_data.next_year,
        UserSubscription.subscription_Month == date_data.next_month
    )
    result = db.execute(stmt)
    sub = result.scalar_one_or_none()
    if sub is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Can't find this subscription data.")
    # 僅需要取消續訂
    if sub.isAddon is True or sub.price == 0:
        stmt = delete(
            UserSubscription
        ).where(
            UserSubscription.userID == user_id,
            UserSubscription.tierID == tier_id,
            UserSubscription.subscription_Year == date_data.next_year,
            UserSubscription.subscription_Month == date_data.next_month
        )
        result = db.execute(stmt)
        db.commit()
        if sub.isAddon:
            print("取消訂閱進階方案")
        else:
            print("取消訂閱0元方案")
        return {"message": "Delete month subscription successfully", "detail": {"user_id": user_id, "tier_id": tier_id, "subscription": {**sub.__dict__}}}
    else:
    # 刪除本月訂閱
        stmt_this = delete(
            UserSubscription
        ).where(
            UserSubscription.userID == user_id,
            UserSubscription.tierID == tier_id,
            UserSubscription.subscription_Year == date_data.this_year,
            UserSubscription.subscription_Month == date_data.this_month
        )
        result = db.execute(stmt_this)
        print("刪除本月標準訂閱")
        # 刪除次月訂閱(避免跨年錯誤分兩段)
        stmt_next = delete(
            UserSubscription
        ).where(
            UserSubscription.userID == user_id,
            UserSubscription.tierID == tier_id,
            UserSubscription.subscription_Year == date_data.next_year,
            UserSubscription.subscription_Month == date_data.next_month
        )
        result = db.execute(stmt_next)
        print("刪除次月標準訂閱")
        db.commit()

        # 查找0元
        stmt = select(
            Tier
        ).where(
            Tier.creatorID == sub.creatorID,
            Tier.price == 0
        )
        result = db.execute(stmt)
        tier_free = result.scalar_one_or_none()
        if tier_free is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Can't find this subscription data.")
        # 回訂0元
        stmt = insert(UserSubscription).values(
            userID=user_id,
            creatorID=tier_free.creatorID,
            tierID=tier_free.tierID,
            subscription_Year=date_data.this_year,
            subscription_Month=date_data.this_month,
            createTime=datetime.now(tz=timezone.utc),
            price=tier_free.price,
            IsPay=True,
            isAddon=tier_free.isAddon,
            isRenew=False
        )
        result = db.execute(stmt)
        # 續訂0元
        stmt = insert(UserSubscription).values(
            userID=user_id,
            creatorID=tier_free.creatorID,
            tierID=tier_free.tierID,
            subscription_Year=date_data.next_year,
            subscription_Month=date_data.next_month,
            createTime=datetime.now(tz=timezone.utc),
            price=tier_free.price,
            IsPay=False,
            isAddon=tier_free.isAddon,
            isRenew=True
        )
        result = db.execute(stmt)
        db.commit()
        print("回訂0元方案")
        
        return {"message": "Next month subscription delete successfully", "detail": {"user_id": user_id, "tier_id": tier_id}}

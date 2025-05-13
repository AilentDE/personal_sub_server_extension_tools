from config.database import engine, SessionLocal, get_db
from config.setting import settings
from model.UserModels import UserData, CreatorType
from model.WorkModels import Work
from model.OrderModels import Order
from model.PorjectModels import Project
from model.SubscriptionModels import UserSubscription, UserSubscriptionPurview
from util.teams import send_message
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from sqlalchemy import select, func
import pandas as pd

def week_report(force_datetime:datetime|None = None):
    
    # 設定變數
    if not force_datetime:
        target_datetime = datetime.now()
    this_year = target_datetime.strftime('%Y')
    this_month = target_datetime.strftime('%m')
    past_year = (target_datetime-relativedelta(months=1)).strftime('%Y')
    past_month = (target_datetime-relativedelta(months=1)).strftime('%m')
    job_db = SessionLocal()
    message = ""

    # 1.週報
    message += f"{target_datetime.strftime('%Y-%m-%d')} 週報:\n\n"
    ## 營業額
    stmt = select(func.coalesce(func.sum(Order.orderFee), 0).label('turnover')).where(Order.orderStatus == 'completed')
    result = job_db.execute(stmt).scalar_one()
    message += f"- **營業額: {result}**\r"
    ## 會員總數
    stmt = select(func.count(UserData.userID).label('user_count'))
    result = job_db.execute(stmt).scalar_one()
    message += f"- **會員總數: {result}**\r"
    ## 創作者總數
    stmt = select(func.count(UserData.userID).label('creator_count')).where(UserData.isWork == True)
    result = job_db.execute(stmt).scalar_one()
    message += f"- **創作者總數: {result}**\r"
    ## 公開作品總數
    stmt = select(func.count(Work.workID).label('work_count')).where(Work.publicSetting.in_(['everyone', 'tiers']), Work.isDelete == False)
    result = job_db.execute(stmt).scalar_one()
    message += f"- **作品總數: {result}**\r"
    ## 企劃總數
    stmt = select(func.count(Project.activityID).label('project_count')).where(Project.isDelete == False)
    result = job_db.execute(stmt).scalar_one()
    message += f"- **企劃總數: {result}**\r"

    # 2.訂閱狀況
    message += '\n\n訂閱狀況:\n\n'
    ## 取表:
    with engine.connect() as conn:
        ### 當月權力表
        stmt = select(UserSubscriptionPurview).where(
            UserSubscriptionPurview.subscription_Year == this_year,
            UserSubscriptionPurview.subscription_Month == this_month,
            UserSubscriptionPurview.price != 0
        ).order_by(
            UserSubscriptionPurview.userID,
            UserSubscriptionPurview.creatorID,
            UserSubscriptionPurview.price.desc()
        )
        df_purview = pd.read_sql(stmt, conn)
        df_purview_normal = df_purview[df_purview['isAddon'] == False].copy()
        df_purview_normal.drop_duplicates(['userID', 'creatorID'], inplace=True)
        df_purview_addon = df_purview[df_purview['isAddon'] == True].copy()
        ### 前月權力表
        stmt = select(UserSubscriptionPurview).where(
            UserSubscriptionPurview.subscription_Year == past_year,
            UserSubscriptionPurview.subscription_Month == past_month,
            UserSubscriptionPurview.price != 0
        ).order_by(
            UserSubscriptionPurview.userID,
            UserSubscriptionPurview.creatorID,
            UserSubscriptionPurview.price.desc()
        )
        df_purview_past = pd.read_sql(stmt, conn)
        df_purview_past_normal = df_purview_past[df_purview_past['isAddon'] == False].copy()
        df_purview_past_normal.drop_duplicates(['userID', 'creatorID'], inplace=True)
        df_purview_past_addon = df_purview_past[df_purview_past['isAddon'] == True].copy()
        ### 當月訂閱表
        stmt = select(UserSubscription).where(
            UserSubscription.subscription_Year == this_year,
            UserSubscription.subscription_Month == this_month,
            UserSubscription.IsPay == True
        ).order_by(
            UserSubscription.userID,
            UserSubscription.creatorID,
            UserSubscription.price.desc()
        )
        df_subscription = pd.read_sql(stmt, engine)
        df_subscription_normal = df_subscription[df_subscription['isAddon'] == False].copy()
        df_subscription_addon = df_subscription[df_subscription['isAddon'] == True].copy()
    ## 當月總訂閱金額、人數
    message += "- **當月總訂閱金額: {}**\r".format(pd.concat([df_purview_normal.price, df_purview_addon.price], axis=0).sum())
    message += "- **當月總訂閱人數: {}**\r".format(len(pd.concat([df_purview_normal.userID, df_purview_addon.userID], axis=0).unique()))
    ## 新訂閱的金額、人數
    ### 標準: 這個月有權力，上個月沒有
    temp_normal = pd.merge(df_purview_normal, df_purview_past_normal, how='left', on=['userID', 'creatorID'])
    temp_normal = temp_normal[temp_normal['createTime_y'].isnull()]
    ### 進階: 這個月有權力，上個月沒有
    temp_addon = pd.merge(df_purview_addon, df_purview_past_addon, how='left', on=['userID', 'creatorID', 'tierID'])
    temp_addon = temp_addon[temp_addon['createTime_y'].isnull()]

    message += '- **當月新訂閱金額: {}**\r'.format(temp_normal['price_x'].sum() + temp_addon['price_x'].sum())
    message += '- **當月新訂閱人數: {}**\r'.format(len(pd.concat([temp_normal.userID, temp_addon.userID], axis=0).unique()))
    ## 預計取消訂閱的金額、人數
    ### 標準: 有權力，但訂閱為0元方案
    df_subscription_normal = df_subscription_normal[df_subscription_normal['price'] == 0]
    temp_normal = pd.merge(df_purview_normal, df_subscription_normal, how='left', on=['userID', 'creatorID'])
    temp_normal = temp_normal[temp_normal['IsPay'].notnull()]
    ### 進階: 有權利，但無訂閱
    temp_addon = pd.merge(df_purview_addon, df_subscription_addon, how='left', on=['userID', 'creatorID', 'tierID'])
    temp_addon = temp_addon[temp_addon['IsPay'].isnull()]

    message += '- **當月取消訂閱金額: {}**\r'.format(temp_normal['price_x'].sum() + temp_addon['price_x'].sum())
    message += '- **當月取消訂閱人數: {}**\r'.format(len(pd.concat([temp_normal.userID, temp_addon.userID], axis=0).unique()))
    
    # 3.創作者類別分布
    message += '\n\n創作者的類別分布\n\n'

    stmt = select(
        CreatorType.typeID,
        func.count(CreatorType.typeID).label('creatorTypeCount')
    ).group_by(CreatorType.typeID)
    results = job_db.execute(stmt).all()
    for typeID, creatorTypeCount in results:
        message += f"- **{typeID}**: {creatorTypeCount}\r"
    # 4.作品類別分布
    message += '\n\n作品的類別分布\n\n'

    stmt = select(
        Work.typeID,
        func.count(Work.typeID).label('workTypeCount')
    ).where(
        Work.isDelete == False,
        Work.publicSetting != 'self'
    ).group_by(Work.typeID)
    results = job_db.execute(stmt).all()
    for typeID, creatorTypeCount in results:
        message += f"- **{typeID}**: {creatorTypeCount}\r"

    job_db.close()
    # teams
    message = [
        {
        "type": "TextBlock",
        "text": message
        }
    ]
    r = send_message(message, token=settings.teams_week_report)

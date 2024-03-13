from config.database import engine, SessionLocal, get_db
from config.setting import settings
from model.UserModels import UserData, CreatorType
from model.WorkModels import Work
from model.OrderModels import Order
from model.PorjectModels import Project
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
    past_year = (target_datetime-relativedelta(months=1)).strftime('%m')
    job_db = SessionLocal()
    message = ""

    # 1.週報
    message += f"{target_datetime.strftime('%Y-%m-%d')} 週報:\n\n"
    ## 營業額
    stmt = select(func.coalesce(func.sum(Order.orderFee), 0).label('turnover')).filter(Order.orderStatus == 'completed')
    result = job_db.execute(stmt).scalar_one()
    message += f"- **營業額: {result}**\r"
    ## 會員總數
    stmt = select(func.count(UserData.userID).label('user_count'))
    result = job_db.execute(stmt).scalar_one()
    message += f"- **會員總數: {result}**\r"
    ## 創作者總數
    stmt = select(func.count(UserData.userID).label('creator_count')).filter(UserData.isWork == True)
    result = job_db.execute(stmt).scalar_one()
    message += f"- **創作者總數: {result}**\r"
    ## 公開作品總數
    stmt = select(func.count(Work.workID).label('work_count')).filter(Work.publicSetting.in_(['everyone', 'tiers']), Work.isDelete == False)
    result = job_db.execute(stmt).scalar_one()
    message += f"- **作品總數: {result}**\r"
    ## 企劃總數
    stmt = select(func.count(Project.activityID).label('project_count')).filter(Project.isDelete == False)
    result = job_db.execute(stmt).scalar_one()
    message += f"- **企劃總數: {result}**\r"

    # 2.訂閱狀況
    # 3.創作者類別分布
    # 4.作品類別分布
    job_db.close()
    # teams
    message = [
        {
        "type": "TextBlock",
        "text": message
        }
    ]
    r = send_message(message, token=settings.teams_week_report)

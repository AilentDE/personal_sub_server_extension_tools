from config.database import engine
from config.setting import settings
from model.UserModels import UserCashRecord
from sqlalchemy import select
import pandas as pd
from datetime import datetime, date, timedelta
import json
import tempfile
import requests
from util.teams import send_message

with open('./job/specialUsers.json', 'r', encoding='utf-8') as file:
    special_users = json.load(file)

def report_receivable(user_set_name:str, force_target_datetime:datetime|None = None):
    match user_set_name:
        case 'lucselene':
            target_date = date.today() - timedelta(days=30)
            target_datetime = datetime(target_date.year, target_date.month, 12)-timedelta(hours=8)+timedelta(minutes=10) #漢龍有1天誤差+結算作業時差
        case 'proxima':
            target_date = date.today()
            target_datetime = datetime(target_date.year, target_date.month, 12)-timedelta(hours=8)+timedelta(minutes=10) #漢龍有1天誤差+結算作業時差
        case 'normal':
            target_date = date.today()
            target_datetime = datetime(target_date.year, target_date.month, 12)-timedelta(hours=8)+timedelta(minutes=10) #漢龍有1天誤差+結算作業時差
    if force_target_datetime:
        target_datetime = force_target_datetime
    print('Report Receivable', user_set_name, target_datetime.isoformat()+'Z')
    stmt = select(
        UserCashRecord.rowID.label('id'),
        UserCashRecord.userID.label('userId'),
        UserCashRecord.cashType.label('type'),
        UserCashRecord.orderFee,
        UserCashRecord.platformFee,
        UserCashRecord.cashFee,
        UserCashRecord.netProfit,
        UserCashRecord.status,
        UserCashRecord.createTime.label('createdAt'),
        UserCashRecord.memo
    ).where(
        UserCashRecord.cashType.in_(['withdraw', 'auto-withdraw']),
        UserCashRecord.status == 'pending',
        UserCashRecord.createTime < target_datetime
    )
    if user_set_name == 'normal':
        user_set = {**special_users['lucselene'], **special_users['proxima']}
        stmt = stmt.where(UserCashRecord.userID.notin_(user_set.keys()))
    else:
        user_set = special_users[user_set_name]
        stmt = stmt.where(UserCashRecord.userID.in_(user_set.keys()))
    # data
    with engine.connect() as conn:
        df = pd.read_sql_query(stmt, conn)
        print(df)
        temp_file = tempfile.NamedTemporaryFile(suffix='.xlsx', delete=False)
        df.to_excel(temp_file.name, index=False)
    # requests
    ## csrf
    r = requests.post(settings.api_uri+'/api/Admin/csrf_token')# 路徑之後會更新成.../Admins/...
    csrf_token = r.json()['csrfToken']
    ## login
    r = requests.post(
        settings.api_uri+'/api/Admins/Login',
        headers={"X-XSRF-TOKEN": csrf_token},
        json={"account": settings.api_account, "password": settings.api_password}
        )
    access_token = r.json()['accessToken']
    ## post excel
    with open(temp_file.name, 'rb') as fp:
        r = requests.post(
            settings.api_uri+'/api/Admins/receivables/upload_transfer_results',
            headers={"X-XSRF-TOKEN": csrf_token, "Authorization": f"Bearer {access_token}"},
            files={'excelFile': fp}
        )
    if r.status_code == 200:
        print(f'[{datetime.now().isoformat()}Z] 提交金流回報成功')
    else:
        print(f'[{datetime.now().isoformat()}Z] 提交金流回報失敗')
    # teams
    message = [
        {
            "type": "TextBlock",
            "text": f"已回報 {user_set_name} {target_datetime.month} 月份應付帳款明細"
        }
    ]
    r = send_message(message)
from config.database import engine
from config.boto3 import s3
from config.setting import settings
from model.UserModels import UserRealData, UserCashRecord
from sqlalchemy import select
import pandas as pd
from util.teams import send_message
import tempfile
from datetime import date, timedelta

def account_payable():
    stmt = select(
        UserCashRecord.rowID.label('id'),
        UserCashRecord.cashType.label('type'),
        UserCashRecord.netProfit.label('grossAmount'),
        UserCashRecord.status,
        UserCashRecord.createTime,
        UserCashRecord.memo,
        UserRealData.bankName,
        UserRealData.bankBranchName,
        UserRealData.bankNo,
        UserRealData.bankAccount,
        UserRealData.userRealName,
        UserRealData.identityNumber
    ).join(
        UserRealData, UserCashRecord.userID == UserRealData.userID
    ).where(
        UserCashRecord.cashType.in_(['withdraw', 'auto-withdraw']),
        UserCashRecord.status == 'pending'
    ).order_by(
        UserCashRecord.createTime
    )
    # data
    with engine.connect() as conn:
        data = pd.read_sql_query(stmt, conn)
        data['createTime'] = data['createTime'].apply(lambda x: x+timedelta(hours=8))
         # excel
        with tempfile.TemporaryFile() as temp_file:
            with pd.ExcelWriter(temp_file, engine='openpyxl') as writer:
                data.to_excel(writer, index=False)
            temp_file.seek(0)
            # S3
            file_name = f'account_payable_{date.today()}.xlsx'
            s3.upload_fileobj(temp_file, settings.aws_bucket_name, file_name)
            s3.put_object_acl(ACL='public-read', Bucket=settings.aws_bucket_name, Key=file_name)
            file_url = f'https://{settings.aws_bucket_name}.s3.amazonaws.com/{file_name}'
    # teams
    message = [
        {
        "type": "TextBlock",
        "text": f"Clusters {date.today().month} 月份應付帳款明細"
        }
    ]
    action = [
        {
        "type": "Action.OpenUrl",
        "title": "下載檔案",
        "url": file_url
        }
    ]
    r = send_message(message, action, mention='BR')

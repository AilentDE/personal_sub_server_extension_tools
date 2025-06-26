from config.database import engine
from config.boto3 import s3
from config.setting import settings
from model.UserModels import UserRealData, UserCashRecord
from sqlalchemy import select
import pandas as pd
from util.teams import send_message
import tempfile
from datetime import date, timedelta
from util.retry_policy import retry_policy


@retry_policy
def account_payable():
    stmt = (
        select(
            UserCashRecord.rowID.label("id"),
            UserCashRecord.cashType.label("type"),
            UserCashRecord.netProfit.label("grossAmount"),
            UserCashRecord.status,
            UserCashRecord.createTime,
            UserCashRecord.memo,
            UserRealData.bankName,
            UserRealData.bankBranchName,
            UserRealData.bankNo,
            UserRealData.bankAccount,
            UserRealData.userRealName,
            UserRealData.identityNumber,
            UserRealData.identityType,
        )
        .join(UserRealData, UserCashRecord.userID == UserRealData.userID)
        .where(
            UserCashRecord.cashType.in_(["withdraw", "auto-withdraw"]),
            UserCashRecord.status == "pending",
        )
        .order_by(UserCashRecord.createTime)
    )
    # data
    with engine.connect() as conn:
        data = pd.read_sql_query(stmt, conn)
        data["createTime"] = data["createTime"].apply(lambda x: x + timedelta(hours=8))

        tw_data = data[data["identityType"] == "taiwan"]
        foreign_data = data[data["identityType"] == "foreigner"]

        teams_actions = []
        # taiwan excel
        if tw_data.shape[0] > 0:
            with tempfile.TemporaryFile() as temp_file:
                with pd.ExcelWriter(temp_file, engine="openpyxl") as writer:
                    tw_data.to_excel(writer, index=False)
                temp_file.seek(0)
                # S3
                file_name = f"account_payable_{date.today()}_tw.xlsx"
                s3.upload_fileobj(temp_file, settings.aws_bucket_name, file_name)
                s3.put_object_acl(
                    ACL="public-read", Bucket=settings.aws_bucket_name, Key=file_name
                )
                tw_file_url = (
                    f"https://{settings.aws_bucket_name}.s3.amazonaws.com/{file_name}"
                )
                teams_actions.append(
                    {
                        "type": "Action.OpenUrl",
                        "title": "台灣應付帳款明細",
                        "url": tw_file_url,
                    }
                )
        # foreign excel
        if foreign_data.shape[0] > 0:
            with tempfile.TemporaryFile() as temp_file:
                with pd.ExcelWriter(temp_file, engine="openpyxl") as writer:
                    foreign_data.to_excel(writer, index=False)
                temp_file.seek(0)
                # S3
                file_name = f"account_payable_{date.today()}_foreign.xlsx"
                s3.upload_fileobj(temp_file, settings.aws_bucket_name, file_name)
                s3.put_object_acl(
                    ACL="public-read", Bucket=settings.aws_bucket_name, Key=file_name
                )
                foreign_file_url = (
                    f"https://{settings.aws_bucket_name}.s3.amazonaws.com/{file_name}"
                )
                teams_actions.append(
                    {
                        "type": "Action.OpenUrl",
                        "title": "外國應付帳款明細",
                        "url": foreign_file_url,
                    }
                )

    # teams
    message = [
        {"type": "TextBlock", "text": f"Clusters {date.today().month} 月份應付帳款明細"}
    ]
    r = send_message(message, teams_actions, mention="BR")
    r.raise_for_status()

import boto3
from config.setting import settings

s3 = boto3.client('s3',
                  aws_access_key_id=settings.aws_access_key,
                  aws_secret_access_key=settings.aws_access_secret)
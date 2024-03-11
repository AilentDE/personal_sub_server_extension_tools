from pydantic_settings import BaseSettings, SettingsConfigDict
import os

from functools import lru_cache

class Settings(BaseSettings):
    aws_access_key:str = os.getenv('AWS_ACCESS_KEY')
    aws_access_secret:str = os.getenv('AWS_ACCESS_SECRET')
    # AWS_REGION:str = os.getenv('AWS_REGION')
    aws_bucket_name:str = os.getenv('AWS_BUCKET_NAME')
    mssql_url:str = os.getenv('MSSQL_URL')
    teams_channel_url:str = os.getenv('TEAMS_CHANNEL_URL')
    api_uri:str = os.getenv('API_URI')
    api_account:str = os.getenv('API_ACCOUNT')
    api_password:str = os.getenv('API_PASSWORD')

    model_config = SettingsConfigDict(env_file=".env")

@lru_cache
def get_settings():
    return Settings()

settings = get_settings()
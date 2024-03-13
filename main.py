from fastapi import FastAPI
# from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from job import report_receivable, account_payable, week_report
from route import work, user
from datetime import datetime

@asynccontextmanager
async def lifespan(app: FastAPI):
    scheduler = AsyncIOScheduler()
    scheduler.add_job(account_payable, CronTrigger(day=12, hour=12, minute=0, second=0)) #結算名單
    scheduler.add_job(report_receivable, CronTrigger(day='Last', hour=12, minute=0, second=0), args=['proxima']) #回報proxima名單
    scheduler.add_job(report_receivable, CronTrigger(day=10, hour=12, minute=0, second=0), args=['lucselene']) #回報lucselene名單
    print('scheduler start ...')
    scheduler.start()
    yield
    print('scheduler shutdown ...')
    scheduler.shutdown()

app = FastAPI(
    title='Clusters extension tools',
    version='0.0.2',
    description='針對管理群編寫的擴充工具，基於安全請勿於本地以外的環境部屬。',
    docs_url='/tools',
    lifespan=lifespan
)

# Only use swagger
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],
#     allow_credentials=True,
#     allow_methods=['GET', 'POST'],
#     allow_headers=["*"],
# )

app.include_router(work.router)
app.include_router(user.router)


@app.get("/")
def read_root():
    # report_receivable('proxima', datetime(2024, 2, 11, 16, 10, 0))
    # account_payable()
    week_report()
    return {"Hello": "World"}

# uvicorn main:app --reload
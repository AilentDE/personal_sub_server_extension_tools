from fastapi import APIRouter
from job.report import week_report
from datetime import datetime

router = APIRouter(
    prefix='/report',
    tags=['Report']
)

@router.get('/weekReport')
async def request_weekly_report(request_datetime: datetime|None = None):
    week_report(request_datetime)
    return {
        "message": "Report sent."
    }
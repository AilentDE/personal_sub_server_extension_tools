from fastapi import APIRouter, HTTPException, status, Depends, UploadFile
from fastapi.responses import FileResponse
from typing import Annotated
from config.database import engine, get_db
from sqlalchemy import select, update
from sqlalchemy.orm import Session
from model.WorkModels import Work
import pandas as pd
from datetime import datetime, timedelta
import tempfile

router = APIRouter(
    prefix='/work',
    tags=['CreatorPost']
)

@router.get('/recomendedList', response_class=FileResponse)
async def get_recomended_work_list():
    stmt = select(Work).where(Work.isRecommended == True).order_by(Work.typeID, Work.publishTime.asc())
    # data
    with engine.connect() as conn:
        data = pd.read_sql_query(stmt, conn)
        data = data[['workID', 'title', 'typeID', 'publishTime']]
        data['publishTime'] = data['publishTime'].apply(lambda x: x+timedelta(hours=8))
        data['url'] = data['workID'].apply(lambda x: 'https://clusters.tw/creator-posts/'+x)
        data.columns = ['id', '標題', '作品類型', '發布時間', 'url']
        # excel
        with tempfile.NamedTemporaryFile(delete=False, suffix='.xlsx') as temp_file:
            data.to_excel(temp_file.name, index=False)
    return FileResponse(path=temp_file.name, filename=f'recommended_work_list_{datetime.now().strftime("%Y%m%d%H%M%S")}.xlsx', media_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')

@router.post('/recomendedList')
async def set_recomended_work_list(db: Annotated[Session, Depends(get_db)], file: UploadFile):
    if file.content_type != 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet':
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Only accept .xlsx file.'
        )
    df = pd.read_excel(file.file)
    if 'id' not in df.columns:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='sheet must have column [id].'
        )
    recommended_ids = df['id'].tolist()

    # remove recommended
    stmt = update(Work).where(Work.isRecommended == True).values(isRecommended = False)
    result = db.execute(stmt)
    db.commit()

    # set recommended
    stmt = update(Work).where(
        Work.isDelete == False,
        Work.workID.in_(recommended_ids)
    ).values(isRecommended = True)
    result = db.execute(stmt)
    db.commit()

    return {"message": "Works recommended successfully"}

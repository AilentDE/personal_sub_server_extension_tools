from fastapi import APIRouter, Query
from fastapi.responses import FileResponse
from sqlalchemy import select, func
from model.UserModels import UserData, CreatorType
from config.database import engine
import pandas as pd
from datetime import datetime, timedelta
import tempfile

router = APIRouter(
    prefix='/user',
    tags=['Users']
)

@router.get("/userData")
async def get_user_data(
    creator_types: list[str]= Query(default=['illustration', 'comic', 'cosplay', 'sound', 'game', 'model', 'other', 'none'],
                                   description='options of illustration, comic, cosplay, sound, game, model, other or **none** .'),
    created_from: datetime|None = Query(default=None,
                                        description='YYYY-MM-DDTHH:mm:ssZ \(UTC+0\)'),
    created_until: datetime|None = Query(default=None,
                                         description='YYYY-MM-DDTHH:mm:ssZ \(UTC+0\)')):
    print(creator_types)
    stmt = select(
        UserData.userID,
        UserData.displayName,
        UserData.email,
        UserData.createdAt,
        func.aggregate_strings(CreatorType.typeID, ',').label('creatorFields')
    ).join(CreatorType, UserData.userID == CreatorType.creatorID, isouter=True)
    if 'none' not in creator_types:
        stmt = stmt.where(CreatorType.typeID.in_(creator_types))
    elif creator_types == ['none']:
        stmt = stmt.where(CreatorType.typeID==None)
    if created_from:
        stmt = stmt.where(UserData.createdAt > created_from)
    if created_until:
        stmt = stmt.where(UserData.createdAt <= created_until)
    stmt = stmt.group_by(UserData.userID, UserData.displayName, UserData.email, UserData.createdAt).order_by(UserData.createdAt.asc())
    # data
    with engine.connect() as conn:
        data = pd.read_sql_query(stmt, conn)
        def check_creator_type(types_string:str|None, type:str):
            if types_string is None:
                return 0
            elif type in types_string:
                return 1
            else:
                return 0
        data['createdAt'] = data['createdAt'].apply(lambda x: x+timedelta(hours=8))
        data['illustration'] = data['creatorFields'].apply(lambda x: check_creator_type(x, 'illustration'))
        data['comic'] = data['creatorFields'].apply(lambda x: check_creator_type(x, 'comic'))
        data['cosplay'] = data['creatorFields'].apply(lambda x: check_creator_type(x, 'cosplay'))
        data['sound'] = data['creatorFields'].apply(lambda x: check_creator_type(x, 'sound'))
        data['game'] = data['creatorFields'].apply(lambda x: check_creator_type(x, 'game'))
        data['model'] = data['creatorFields'].apply(lambda x: check_creator_type(x, 'model'))
        data['other'] = data['creatorFields'].apply(lambda x: check_creator_type(x, 'other'))
        # excel
        with tempfile.NamedTemporaryFile(delete=False, suffix='.xlsx') as temp_file:
            data.to_excel(temp_file.name, index=False)
    return FileResponse(path=temp_file.name, filename=f'user_list_{datetime.now().strftime("%Y%m%d%H%M%S")}.xlsx', media_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
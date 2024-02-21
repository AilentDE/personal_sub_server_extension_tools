from fastapi import FastAPI
# from fastapi.middleware.cors import CORSMiddleware
from route import work, user

app = FastAPI(
    title='Clusters extension tools',
    version='0.0.1',
    description='針對管理群編寫的擴充工具，基於安全請勿於本地以外的環境部屬。',
    docs_url='/tools'
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
    return {"Hello": "World"}

# uvicorn main:app --reload
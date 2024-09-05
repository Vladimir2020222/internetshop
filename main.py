from fastapi import FastAPI
from accounts import router as accounts_router

app = FastAPI()
app.include_router(accounts_router)

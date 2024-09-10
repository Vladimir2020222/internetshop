from fastapi import FastAPI
from accounts import router as accounts_router
from cart import router as cart_router

app = FastAPI()
app.include_router(accounts_router)
app.include_router(cart_router)

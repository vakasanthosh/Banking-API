from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from app.database import Base, engine
from app import models
from routers.users import router as user_router
from routers.banking import router as banking_router

app = FastAPI()

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code = 500,
        content={
            "detail": "Internal Server Error"
        }
    )

Base.metadata.create_all(bind = engine)
app.include_router(user_router)
app.include_router(banking_router)

@app.get("/")
def home():
    return {"message": "welcome to Banking API"}
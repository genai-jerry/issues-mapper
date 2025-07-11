from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.requests import Request
from core.database import engine, Base
from api.routes import router as api_router
from core.background_processor import processor

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

@app.on_event("startup")
async def on_startup():
    Base.metadata.create_all(bind=engine)
    # Resume any incomplete jobs on server startup
    await processor.resume_incomplete_jobs()

app.include_router(api_router)

@app.get("/")
def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request}) 
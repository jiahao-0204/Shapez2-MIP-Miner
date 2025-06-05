# system
from pathlib import Path
from uuid import uuid4

# third party
from fastapi import FastAPI, UploadFile, Form, BackgroundTasks, Request
from fastapi.responses import PlainTextResponse, HTMLResponse

from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

app = FastAPI()


# Serve static files (e.g. output images)
app.mount("/static", StaticFiles(directory="static"), name="static")

# Templates setup
templates = Jinja2Templates(directory="templates")


# @app.get("/", response_class=PlainTextResponse)
# async def get_root():
#     return "Hello World!"

@app.get("/", response_class=HTMLResponse)
async def get_index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

def process_data(task_id : str, tmp_path : Path, clicks : str):
    print(f"Processing task {task_id} with file {tmp_path} and clicks {clicks}")
    
@app.post("/uploads/")
async def post_uploads(
    file: UploadFile,
    background_tasks: BackgroundTasks,
    clicks: str = Form(...),
    ):
    
    # create a unique task id
    task_id = uuid4().hex
    
    # save file to temp location and pass the path to the background task
    filename = file.filename or ""
    suffix = Path(filename).suffix if filename else ""
    tmp_path = Path(f"/tmp/{uuid4()}{suffix}")
    file_content = await file.read()
    with tmp_path.open("wb") as f:
        f.write(file_content)
        
    # add the task to the background tasks
    background_tasks.add_task(process_data, task_id, tmp_path, clicks)
    
    # return the response
    return {"task_id": task_id}
# system
from pathlib import Path
from uuid import uuid4

# third party
from fastapi import FastAPI, UploadFile, File, Form, BackgroundTasks, Request
from fastapi.responses import PlainTextResponse, HTMLResponse, JSONResponse, FileResponse

from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

# ------------------------------------------
# Setup
# ------------------------------------------

# initialize the FastAPI app
app = FastAPI()

# static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# templates
templates = Jinja2Templates(directory="templates")


# ------------------------------------------
# Web API
# ------------------------------------------

# home page
@app.get("/", response_class=HTMLResponse)
async def get_index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

# background task
def process_data(task_id : str, tmp_path : Path, clicks : str):
    print(f"Processing task {task_id} with file {tmp_path} and clicks {clicks}")

# send clicks
@app.post("/send_clicks/", response_class=FileResponse)
async def send_clicks(task_id: str = Form(...), x: float = Form(...), y: float = Form(...), left: bool = Form(...)):
    # log
    print(f"Received clicks for task {task_id}: x={x}, y={y}, left={left}")

    # check if image path exists
    image_path = Path(f"/tmp/{task_id}.png")
    if not image_path.exists():
        return JSONResponse(status_code=404, content={"error": "Image not found"})
    print(f"Image path: {image_path}")
    
    # return the image file
    return FileResponse(image_path, media_type="image/png")    

# get task id
@app.post("/get_task_id/", response_class=JSONResponse)
async def get_task_id(file: UploadFile = File(...)):
    # log
    print(f"Received file: {file.filename}")
    
    # throw an error if the file is not provided
    if not file.filename:
        return JSONResponse(status_code=400, content={"error": "file.filename not found"})
    
    # create task id
    task_id = uuid4().hex
    
    # create a temporary file path
    suffix = Path(file.filename).suffix
    file_path = Path(f"/tmp/{task_id}{suffix}")

    # save the file to the temporary location
    with file_path.open("wb") as f:
        f.write(await file.read())
    
    # log the file path
    print(f"File saved to: {file_path}")

    # return the task_id as json response
    response = JSONResponse(status_code=200, content={"task_id": task_id})
    
    # log the response
    print(f"Response: {bytes(response.body).decode('utf-8')}")
    
    # return
    return response    
    
    # # create a unique task id
    # task_id = uuid4().hex
    
    # # save file to temp location and pass the path to the background task
    # filename = file.filename or ""
    # suffix = Path(filename).suffix if filename else ""
    # tmp_path = Path(f"/tmp/{uuid4()}{suffix}")
    # file_content = await file.read()
    # with tmp_path.open("wb") as f:
    #     f.write(file_content)
        
    # # add the task to the background tasks
    # background_tasks.add_task(process_data, task_id, tmp_path, clicks)
    
    # # return the response
    # return {"task_id": task_id}
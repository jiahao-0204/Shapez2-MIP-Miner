# system
from pathlib import Path
from uuid import uuid4
from io import BytesIO
from zipfile import ZipFile
import base64

# third party
from fastapi import FastAPI, UploadFile, File, Form, BackgroundTasks, Request
from fastapi.responses import PlainTextResponse, HTMLResponse, JSONResponse, FileResponse, StreamingResponse

from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

import cv2

# project
from astroid_parser import AstroidParser
from astroid_optimizer import AstroidOptimizer

# ------------------------------------------
# Setup
# ------------------------------------------

# initialize the FastAPI app
app = FastAPI()

# static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# templates
templates = Jinja2Templates(directory="templates")

# list of tasks
tasks : dict[str, AstroidParser] = {}

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
@app.post("/send_clicks/")
async def send_clicks(task_id: str = Form(...), x: int = Form(...), y: int = Form(...), left: bool = Form(...)):
    # --- log ---
    print(f"Received clicks for task {task_id}: x={x}, y={y}, left={left}")
    # -----------

    # check if image path exists
    image_path = Path(f"/tmp/{task_id}.png")
    if not image_path.exists():
        return JSONResponse(status_code=404, content={"error": "Image not found"})
    
    # --- log ---
    print(f"Image path: {image_path}")
    # -----------
    
    # send clicks to the parser
    if task_id in tasks:
        parser = tasks[task_id]
        parser.add_click(x, y, left)
        print(f"Click added to task {task_id}: x={x}, y={y}, left={left}")
    else:
        print(f"Task {task_id} not found. Cannot add click.")
        return JSONResponse(status_code=404, content={"error": "Task not found"})
    
    # get updated image from the parser
    preview_image = tasks[task_id].request_preview_image()
    simple_coordinate_image = tasks[task_id].request_simple_coordinates_image()
        
    # # Create a zip in memory
    # zip_buffer = BytesIO()
    # with ZipFile(zip_buffer, "w") as zip_file:
    #     if preview_image is not None:
    #         zip_file.writestr("preview.png", preview_image.read())
    #     if simple_coordinate_image is not None:
    #         zip_file.writestr("coordinates.png", simple_coordinate_image.read())
    # zip_buffer.seek(0)

    # return StreamingResponse(zip_buffer, media_type="application/zip", headers={"Content-Disposition": f"attachment; filename={task_id}_results.zip"})
    
    preview_b64 = base64.b64encode(preview_image.read()).decode() if preview_image else None
    simple_b64 = base64.b64encode(simple_coordinate_image.read()).decode() if simple_coordinate_image else None

    return {
        "task_id": task_id,
        "preview_image": preview_b64,
        "simple_coordinate_image": simple_b64
    }
        

# get task id
@app.post("/add_task/", response_class=JSONResponse)
async def add_task(file: UploadFile = File(...)):
    # --- log ---
    print(f"Received file: {file.filename}")
    # -----------
    
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
    
    # --- log ---
    print(f"File saved to: {file_path}")
    # -----------

    # add to task list
    # convert file to cv2 BGR image
    img_bgr = cv2.imread(str(file_path))
    if img_bgr is None:
        return JSONResponse(status_code=415, content={"error": "Invalid image format or corrupted file"})

    # store in task dictionary or your object
    tasks[task_id] = AstroidParser(img_bgr=img_bgr)
    
    # return the task_id as json response
    response = JSONResponse(status_code=200, content={"task_id": task_id})
    
    # --- log ---
    print(f"Response: {bytes(response.body).decode('utf-8')}")
    # -----------
    
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

# run optimizer
@app.post("/run_optimizer/", response_class=JSONResponse)
async def run_optimizer(task_id: str = Form(...)):
    # --- log ---
    print(f"Running optimizer for task {task_id}")
    # -----------
    
    # check if task exists
    if task_id not in tasks:
        return JSONResponse(status_code=404, content={"error": "Task not found"})
    
    astroid_optimizer = AstroidOptimizer()
    
    astroid_location = tasks[task_id].get_simple_coordinates()
    if astroid_location is None:
        return JSONResponse(status_code=400, content={"error": "No astroid location found for the task"})
    
    astroid_optimizer.set_up_model(astroid_location=astroid_location)
    astroid_optimizer.solve_problem()
    
    # get the solution image
    solution_image = astroid_optimizer.get_rendered_image()
    
    if solution_image is None:
        return JSONResponse(status_code=500, content={"error": "Failed to generate solution image"})
    
    # convert to base64
    solution_b64 = base64.b64encode(solution_image.getvalue()).decode()
    
    # get blue print
    blueprint = astroid_optimizer.get_blueprint()
    
    if blueprint is None:
        return JSONResponse(status_code=500, content={"error": "Failed to generate blueprint"})
    
    return {
        "task_id": task_id,
        "solution_image": solution_b64,
        "blueprint": blueprint
    }
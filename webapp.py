# system
from pathlib import Path
from uuid import uuid4
from io import BytesIO
from zipfile import ZipFile
import base64
from contextlib import redirect_stdout
import io
import asyncio
import threading

# third party
from fastapi import FastAPI, UploadFile, File, Form, BackgroundTasks, Request
from fastapi.responses import PlainTextResponse, HTMLResponse, JSONResponse, FileResponse, StreamingResponse

from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

import cv2

# project
from astroid_parser import AstroidParser
from astroid_solver import AstroidSolver

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
tasks_parsers : dict[str, AstroidParser] = {}
tasks_solvers : dict[str, AstroidSolver] = {}

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
    # -----------------------------
    # local processing
    # -----------------------------
    
    # skip if task id not found
    image_path = Path(f"/tmp/{task_id}.png")
    if not image_path.exists():
        return JSONResponse(status_code=404, content={"error": "Image not found"})
    
    # --- log ---
    print(f"Received clicks for task {task_id}: x={x}, y={y}, left={left}")
    print(f"Image path: {image_path}")
    # -----------
    
    # -----------------------------
    # send data to the parser
    # -----------------------------
    parser = tasks_parsers[task_id]
    parser.add_click(x, y, left)
    
    # -----------------------------
    # response ok
    # -----------------------------
    return JSONResponse(status_code=200, content={"message": "Click added successfully"})
            
@app.post("/increase_threshold/", response_class=JSONResponse)
async def increase_threshold(task_id: str = Form(...)):
    # -----------------------------
    # local processing
    # -----------------------------
    
    # skip if task id not found
    if task_id not in tasks_parsers:
        return JSONResponse(status_code=404, content={"error": "Task not found"})
    
    # --- log ---
    print(f"Increasing threshold for task {task_id}")
    # -----------
    
    # ------------------------------
    # send data to the parser
    # ------------------------------
    parser = tasks_parsers[task_id]
    parser.increase_threshold()
    
    # ------------------------------
    # response ok
    # ------------------------------
    return JSONResponse(status_code=200, content={"message": "Threshold updated successfully"})

@app.post("/decrease_threshold/", response_class=JSONResponse)
async def decrease_threshold(task_id: str = Form(...)):
    # -----------------------------
    # local processing
    # -----------------------------
        
    # skip if task id not found
    if task_id not in tasks_parsers:
        return JSONResponse(status_code=404, content={"error": "Task not found"})
    
    # --- log ---
    print(f"Decreasing threshold for task {task_id}")
    # -----------
    
    # ------------------------------
    # send data to the parser
    # ------------------------------
    parser = tasks_parsers[task_id]
    parser.decrease_threshold()
    
    # ------------------------------
    # response ok
    # ------------------------------
    return JSONResponse(status_code=200, content={"message": "Threshold updated successfully"})
    
# update preview
@app.get("/update_preview/{task_id}", response_class=JSONResponse)
async def update_preview(task_id: str):
    # ------------------------------
    # local processing
    # ------------------------------
    if task_id not in tasks_parsers:
        return JSONResponse(status_code=404, content={"error": "Task not found"})
    
    # --- log ---
    print(f"Updating preview for task {task_id}")
    # -----------
    
    # ------------------------------
    # return data to the client
    # ------------------------------
    parser = tasks_parsers[task_id]
    current_threshold = parser.get_threshold()
    preview_image = parser.request_preview_image()
    simple_coordinate_image = parser.request_simple_coordinates_image()
    preview_b64 = base64.b64encode(preview_image.read()).decode() if preview_image else None
    simple_b64 = base64.b64encode(simple_coordinate_image.read()).decode() if simple_coordinate_image else None

    return {
        "task_id": task_id,
        "preview_image": preview_b64,
        "simple_coordinate_image": simple_b64,
        "current_threshold": current_threshold
    }

# add task
@app.post("/add_task/", response_class=JSONResponse)
async def add_task(file: UploadFile = File(...)):
    # -------------------------------
    # local processing
    # -------------------------------
    
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
    tasks_parsers[task_id] = AstroidParser(img_bgr=img_bgr)
    
    # -------------------------------
    # response to the client
    # -------------------------------
    
    # return the task_id as json response
    response = JSONResponse(status_code=200, content={"task_id": task_id})
    
    # --- log ---
    print(f"Response: {bytes(response.body).decode('utf-8')}")
    # -----------
    
    # return
    return response    

@app.get("/run_solver_and_stream/{task_id}")
async def run_solver_and_stream(task_id: str):
    # ------------------------------
    # local processing
    # ------------------------------
    
    # skip if task id not found
    if task_id not in tasks_parsers:
        async def err_task():
            yield "data: Task not found\n\n"
        return StreamingResponse(err_task(), media_type="text/event-stream")
    
    # skip if no astroid locations
    coords = tasks_parsers[task_id].get_simple_coordinates()
    if coords is None:
        async def err_location():
            yield "data: No astroid locations found\n\n"
        return StreamingResponse(err_location(), media_type="text/event-stream")
    
    # create solver if one does not exist
    if task_id not in tasks_solvers:
        tasks_solvers[task_id] = AstroidSolver()
    
    # add locations to the solver
    solver = tasks_solvers[task_id]
    solver.add_astroid_locations(astroid_location=coords)
    
    # -------------------------------
    # separate thread
    # -------------------------------
    
    # get the queue and loop to handle multithreading
    queue = asyncio.Queue()
    loop = asyncio.get_running_loop()
    
    # run the solver in a separate thread to avoid blocking the event loop
    def separate_thread_run_solver(astroid_solver: AstroidSolver, queue: asyncio.Queue, loop: asyncio.AbstractEventLoop):
        # run solver and redirect output
        
        class StreamToQueue(io.StringIO):
            def __init__(self, queue, loop):
                super().__init__()
                self.queue = queue
                self.loop = loop
                self._buffer = ""

            def write(self, s):
                self._buffer += s
                while "\n" in self._buffer:
                    line, self._buffer = self._buffer.split("\n", 1)
                    self.loop.call_soon_threadsafe(self.queue.put_nowait, f"data: {line}\n\n")
                return len(s)

            def flush(self):
                if self._buffer:
                    self.loop.call_soon_threadsafe(self.queue.put_nowait, f"data: {self._buffer}\n\n")
                    self._buffer = ""

        stream_writer = StreamToQueue(queue, loop)
        with redirect_stdout(stream_writer):
            astroid_solver.run_solver()
            
        # push None so stream() can break the loop
        loop.call_soon_threadsafe(queue.put_nowait, "data: DONE\n\n")
        loop.call_soon_threadsafe(queue.put_nowait, None)
        
    threading.Thread(target=separate_thread_run_solver, args=(solver, queue, loop)).start()

    # -------------------------------
    # current thread
    # -------------------------------
    
    # collect from the queue and yield as a stream
    async def stream():
        while True:
            # get the next line from the queue
            line = await queue.get()
                                    
            # break if None is received
            if line is None:
                break
            
            # skip the line that contains "Academic license"
            if "Academic license" in line:
                continue
            
            # yield the line as a server-sent event
            yield line
            
    return StreamingResponse(stream(), media_type="text/event-stream")

# get solver result
@app.get("/get_solver_results/{task_id}")
async def get_solver_results(task_id: str):    
    # skip if task id not found
    if task_id not in tasks_solvers:
        return JSONResponse(status_code=404, content={"error": "Task not found"})
    
    # get the solver
    astroid_solver = tasks_solvers[task_id]
    
    # get the solution image
    solution_image = astroid_solver.get_solution_image()
    
    if solution_image is None:
        return JSONResponse(status_code=500, content={"error": "Failed to generate solution image"})
    
    # convert to base64
    solution_b64 = base64.b64encode(solution_image.getvalue()).decode()
    
    # get blue print
    blueprint = astroid_solver.get_solution_blueprint()
    
    if blueprint is None:
        return JSONResponse(status_code=500, content={"error": "Failed to generate blueprint"})
    
    return {
        "task_id": task_id,
        "solution_image": solution_b64,
        "blueprint": blueprint
    }
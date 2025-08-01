# system
from datetime import datetime, timedelta
from pathlib import Path
from uuid import uuid4
from io import BytesIO
from zipfile import ZipFile
import base64
from contextlib import redirect_stdout
import io
import asyncio
import threading
from time import time
import logging
logger = logging.getLogger(__name__)

# third party
from fastapi import FastAPI, UploadFile, File, Form, BackgroundTasks, Request
from fastapi.responses import PlainTextResponse, HTMLResponse, JSONResponse, FileResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import numpy as np
import qrcode

# project
from app.astroid_parser import parse_using_blueprint_and_return_image, parse_using_blueprint
from app.astroid_solver import AstroidSolver
from app.blueprint_composer import convert_miner_to_fluid
from app.qr_encoder import content_to_segno_image, content_to_segno_matrix, matrix_to_platform_blueprint, matrix_to_building_blueprint

# ------------------------------------------
# Setup
# ------------------------------------------

# initialize the FastAPI app
app = FastAPI()

# static files
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# path for counter
total_counter_path = str(Path.home() / "fastapi_total_counter.txt")
today_counter_path = str(Path.home() / "fastapi_today_counter.txt")
total_qr_counter_path = str(Path.home() / "fastapi_total_qr_counter.txt")
today_qr_counter_path = str(Path.home() / "fastapi_today_qr_counter.txt")

# templates
templates = Jinja2Templates(directory="app/templates")

# list of tasks
tasks_solvers : dict[str, AstroidSolver] = {}
tasks_timestamps : dict[str, float] = {}
tasks_suffix : dict[str, str] = {}  # to store task type if needed

current_running_tasks_num : int = 0

cleanup_interval = 60  # 1 minute
miners_timelimit_max = 300
saturation_timelimit_max = 300
tasks_lifespan = 900  # 15 minutes
logger.info(f"[Parameters] Cleanup interval: {cleanup_interval} seconds")
logger.info(f"[Parameters] Tasks lifespan: {tasks_lifespan} seconds")
logger.info(f"[Parameters] Timelimit: {miners_timelimit_max} seconds")
logger.info(f"[Parameters] Saturation timelimit: {saturation_timelimit_max} seconds")

def cleanup_tasks():    
    now = time()
    for task_id, timestamp in list(tasks_timestamps.items()):
        duration = now - timestamp
        if duration > tasks_lifespan:
            logger.info(f"[Removing task] - {task_id}")
            
            if task_id in tasks_solvers:
                del tasks_solvers[task_id]
            if task_id in tasks_timestamps:
                del tasks_timestamps[task_id]
            if task_id in tasks_suffix:
                del tasks_suffix[task_id]
            
    # Schedule the next cleanup
    threading.Timer(cleanup_interval, cleanup_tasks).start()  # Run every 60 seconds

cleanup_tasks()  # Start the cleanup process

# === Generic total counter functions ===

def increase_counter(path):
    try:
        with open(path, "r") as f:
            counter = int(f.read())
    except (FileNotFoundError, ValueError):
        counter = 0
    with open(path, "w") as f:
        f.write(f"{counter + 1}")

def get_counter(path):
    try:
        with open(path, "r") as f:
            return int(f.read())
    except (FileNotFoundError, ValueError):
        return 0

# === Daily counter functions ===

def increase_daily_counter(path):
    today = datetime.now().strftime("%Y-%m-%d")
    try:
        with open(path, "r") as f:
            lines = f.readlines()
    except FileNotFoundError:
        lines = []

    found = False
    for i, line in enumerate(lines):
        line = line.strip()
        if not line or ':' not in line:
            continue
        parts = line.split(":")
        if len(parts) != 2:
            continue
        date, counter = parts
        if date == today:
            try:
                counter = int(counter) + 1
            except ValueError:
                counter = 1  # fallback to 1 if corrupted
            lines[i] = f"{date}:{counter}\n"
            found = True
            break

    if not found:
        lines.append(f"{today}:1\n")

    with open(path, "w") as f:
        f.writelines(lines)

def get_daily_counter(path):
    today = datetime.now().strftime("%Y-%m-%d")
    try:
        with open(path, "r") as f:
            lines = f.readlines()
    except FileNotFoundError:
        return 0

    for line in lines:
        line = line.strip()
        if not line or ':' not in line:
            continue
        parts = line.split(":")
        if len(parts) != 2:
            continue
        date, counter = parts
        if date == today:
            try:
                return int(counter)
            except ValueError:
                return 0
    return 0
# ------------------------------------------
# Web API
# ------------------------------------------

# home page
@app.get("/", response_class=HTMLResponse)
async def get_index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

# qr page
@app.get("/qr_encoder", response_class=HTMLResponse)
async def get_qr_encoder(request: Request):
    return templates.TemplateResponse("qr_encoder.html", {"request": request})

@app.get("/get_stats/")
async def get_stats():
    return JSONResponse(status_code=200, content={"tasks_ran_in_total": get_counter(total_counter_path), "tasks_ran_today": get_daily_counter(today_counter_path), "current_running_tasks_num": current_running_tasks_num})

@app.get("/get_qr_stats/")
async def get_qr_stats():
    return JSONResponse(status_code=200, content={"qr_codes_ran_in_total": get_counter(total_qr_counter_path), "qr_codes_ran_today": get_daily_counter(today_qr_counter_path)})

@app.post("/get_simple_coordinates_preview/")
async def get_simple_coordinates_preview(input_blueprint: str = Form(...)):
    # -----------------------------
    # local processing
    # -----------------------------
    
    # parse the blueprint
    try:
        img = parse_using_blueprint_and_return_image(input_blueprint)
    except Exception as e:
        return JSONResponse(status_code=400, content={"error": str(e)})
    
    # convert to base64
    img_b64 = base64.b64encode(img.getvalue()).decode()
    
    # return the image as a response
    return JSONResponse(status_code=200, content={"simple_coordinates_image": img_b64})

@app.get("/get_task_id/")
async def get_task_id():
    # create task id
    task_id = uuid4().hex
    tasks_timestamps[task_id] = time()
    
    # return the task_id as json response
    return JSONResponse(status_code=200, content={"task_id": task_id})

@app.get("/run_solver_and_stream")
async def run_solver_and_stream(
    request: Request,
    task_id: str,
    with_elevator_bool: bool,
    miners_timelimit: float,
    saturation_timelimit: float,
    input_miner_blueprint: str
):
    # ------------------------------
    # local processing
    # ------------------------------
        
    # skip if no astroid locations
    coords = parse_using_blueprint(input_miner_blueprint)
    if coords is None:
        async def err_location():
            yield "data: No astroid locations found\n\n"
        return StreamingResponse(err_location(), media_type="text/event-stream")
    
    # create solver if one does not exist
    if task_id not in tasks_solvers:
        tasks_solvers[task_id] = AstroidSolver()
    
    # add locations to the solver
    solver = tasks_solvers[task_id]
    solver.add_astroid_locations(astroid_location=np.array(coords))
    
    # cap timelimit
    miners_timelimit = max(0, min(miners_timelimit, miners_timelimit_max))
    saturation_timelimit = max(0, min(saturation_timelimit, saturation_timelimit_max))

    # -------------------------------
    # separate thread
    # -------------------------------
    
    # get the queue and loop to handle multithreading
    queue = asyncio.Queue()
    loop = asyncio.get_running_loop()
    
    # run the solver in a separate thread to avoid blocking the event loop
    def separate_thread_run_solver(astroid_solver: AstroidSolver, queue: asyncio.Queue, loop: asyncio.AbstractEventLoop, with_elevator_bool: bool, miners_timelimit: float, saturation_timelimit: float):
        global current_running_tasks_num
        
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

        logger.info(f"[Solver] - start for {task_id}")
        current_running_tasks_num += 1
        stream_writer = StreamToQueue(queue, loop)
        with redirect_stdout(stream_writer):
            astroid_solver.run_solver(
                miners_timelimit=miners_timelimit,
                saturation_timelimit=saturation_timelimit,
                with_elevator=with_elevator_bool
            )
        logger.info(f"[Solver] - finish for {task_id}")
        current_running_tasks_num -= 1
        increase_counter(total_counter_path)
        increase_daily_counter(today_counter_path)

        # push None so stream() can break the loop
        loop.call_soon_threadsafe(queue.put_nowait, "data: DONE\n\n")
        loop.call_soon_threadsafe(queue.put_nowait, None)
        
    threading.Thread(target=separate_thread_run_solver, args=(solver, queue, loop, with_elevator_bool, miners_timelimit, saturation_timelimit)).start()

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

# get solver image
@app.post("/get_solver_results")
async def get_solver_results(task_id: str = Form(...), remove_non_saturated_miners: bool = Form(...)):
    # skip if task id not found
    if task_id not in tasks_solvers:
        return JSONResponse(status_code=404, content={"error": "Task not found"})
    
    # get the solver
    astroid_solver = tasks_solvers[task_id]
    
    # get the solution image
    solution_image = astroid_solver.get_solution_image(remove_non_saturated_miners=remove_non_saturated_miners)
    
    if solution_image is None:
        return JSONResponse(status_code=500, content={"error": "Failed to generate solution image"})
    
    # convert to base64
    solution_b64 = base64.b64encode(solution_image.getvalue()).decode()
    
    return {
        "task_id": task_id,
        "solution_image": solution_b64,
    }
    
# get solver blueprint
@app.post("/generate_blueprint/")
async def generate_blueprint(task_id: str = Form(...), miner_blueprint: str = Form(...), solve_for_fluid: bool = Form(...), remove_non_saturated_miners: bool = Form(...)):
    # skip if task id not found
    if task_id not in tasks_solvers:
        return JSONResponse(status_code=404, content={"error": "Task not found"})
        
    # get the solver
    astroid_solver = tasks_solvers[task_id]
    if astroid_solver is None:
        return JSONResponse(status_code=404, content={"error": "Solver not found"})
    
    # get the blueprint txt
    if miner_blueprint == "empty":
        miner_blueprint = ""
    blueprint = astroid_solver.get_solution_blueprint(miner_blueprint=miner_blueprint, remove_non_saturated_miners=remove_non_saturated_miners)

    if solve_for_fluid:
        new_blueprint = convert_miner_to_fluid(blueprint, miner_blueprint)
        blueprint = new_blueprint

    if blueprint is None:
        return JSONResponse(status_code=500, content={"error": "Failed to generate blueprint"})
            
    return {"blueprint": blueprint}


# ------------------------------------------
# QR encoder
# ------------------------------------------

@app.post("/generate_qr_code_image/")
async def generate_qr_code_image(input_text: str = Form(...), version: str = Form(...), error_correction_level: str = Form(...), boost_error: bool = Form(...)):
    # generate QR code image
    blob, version_used, error_level = content_to_segno_image(input_text, version, error_correction_level, boost_error)

    if version_used == "M1":
        error_level = "L"

    # convert to base64 and create data URL
    img_b64 = base64.b64encode(blob).decode('utf-8')
    img_data_url = f"data:image/png;base64,{img_b64}"
    
    return JSONResponse(status_code=200, content={"qr_code_image": img_data_url, "version_used": version_used, "error_level": error_level})

@app.post("/generate_qr_code_blueprint/")
async def generate_qr_code_blueprint(input_text: str = Form(...), version: str = Form(...), error_correction_level: str = Form(...), boost_error: bool = Form(...), blueprint_type: str = Form(...)):
    # generate QR code matrix
    matrix = content_to_segno_matrix(input_text, version, error_correction_level, boost_error)
    
    # convert to blueprint
    if blueprint_type == "platform":
        blueprint = matrix_to_platform_blueprint(matrix)
    elif blueprint_type == "building":
        blueprint = matrix_to_building_blueprint(matrix)
    
    # increase qr counter
    increase_counter(total_qr_counter_path)
    increase_daily_counter(today_qr_counter_path)

    return JSONResponse(status_code=200, content={"blueprint": blueprint})
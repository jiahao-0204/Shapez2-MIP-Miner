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

# project
from app.astroid_parser import parse_using_blueprint_and_return_image, parse_using_blueprint
from app.astroid_solver import AstroidSolver
from app.blueprint_composer import convert_miner_to_fluid

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

# increase total counter
def increase_total_counter():
    # increase the number stored in the counter file
    with open(total_counter_path, "r") as f:
        counter = int(f.read())
    with open(total_counter_path, "w") as f:
        f.write(f"{counter + 1}")

def get_total_counter():
    # create the file if it does not exist
    if not Path(total_counter_path).exists():
        with open(total_counter_path, "w") as f:
            f.write("0")

    with open(total_counter_path, "r") as f:
        counter = int(f.read())
    return counter

# increase today counter
def increase_today_counter():
    with open(today_counter_path, "r") as f:
        counter = int(f.read())
    with open(today_counter_path, "w") as f:
        f.write(f"{counter + 1}")

def get_today_counter():
    # create the file if it does not exist
    if not Path(today_counter_path).exists():
        with open(today_counter_path, "w") as f:
            f.write("0")

    with open(today_counter_path, "r") as f:
        counter = int(f.read())
    return counter

def reset_today_counter():
    with open(today_counter_path, "w") as f:
        f.write("0")

def reset_stats_at_midnight():
    try:
        # get current time
        now = datetime.now()
        
        # Check if we're within the first minute of midnight
        if now.hour == 0 and now.minute == 0:
            try:
                reset_today_counter()
                logger.info("[Stats] Successfully reset daily counter at midnight")
            except Exception as e:
                logger.error(f"[Stats] Failed to reset counter: {str(e)}")
        
        # Schedule next check
        next_midnight = now.replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(days=1)
        time_to_midnight = (next_midnight - now).total_seconds()
        
        # Ensure we don't schedule a negative time
        if time_to_midnight <= 0:
            time_to_midnight = 24 * 3600  # Schedule for next day if we somehow got a negative time
        
        # Schedule next check
        threading.Timer(time_to_midnight, reset_stats_at_midnight).start()
        
    except Exception as e:
        logger.error(f"[Stats] Error in reset_stats_at_midnight: {str(e)}")
        # Try to recover by scheduling another attempt in 1 hour
        threading.Timer(3600, reset_stats_at_midnight).start()

# Start the reset process
reset_stats_at_midnight()

# ------------------------------------------
# Web API
# ------------------------------------------

# home page
@app.get("/", response_class=HTMLResponse)
async def get_index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/get_stats/")
async def get_stats():
    return JSONResponse(status_code=200, content={"tasks_ran_in_total": get_total_counter(), "tasks_ran_today": get_today_counter(), "current_running_tasks_num": current_running_tasks_num})

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
        increase_total_counter()
        increase_today_counter()

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
    
    return {
        "task_id": task_id,
        "solution_image": solution_b64,
    }
    
# get solver blueprint
@app.post("/generate_blueprint/")
async def generate_blueprint(task_id: str = Form(...), miner_blueprint: str = Form(...), solve_for_fluid: bool = Form(...)):
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
    blueprint = astroid_solver.get_solution_blueprint(miner_blueprint=miner_blueprint)

    if solve_for_fluid:
        new_blueprint = convert_miner_to_fluid(blueprint, miner_blueprint)
        blueprint = new_blueprint

    if blueprint is None:
        return JSONResponse(status_code=500, content={"error": "Failed to generate blueprint"})
            
    return {"blueprint": blueprint}
// -----------------------------------------------
// data
// -----------------------------------------------
let leftClicks = [];
let rightClicks = [];
let task_id = null;

// -----------------------------------------------
// get web page elements
// -----------------------------------------------
const button_upload_file = document.getElementById('fileInput'); 
const button_submit_image = document.getElementById('submit_image');
const button_run_solver = document.getElementById('run_solver');
const canvas_preview = document.getElementById('canvas');
const canvas_simple_coordinates = document.getElementById('simple_coordinates_canvas');
const canvas_results = document.getElementById('result_canvas');

const button_copy_blueprint = document.getElementById('copy_blueprint');
const text_blueprint = document.getElementById('blueprint_text');

// -----------------------------------------------
// setup elements
// -----------------------------------------------
const preview_canvas_width = 800;
canvas_preview.style.width = `${preview_canvas_width}px`;
canvas_preview.style.height = 'auto'; // set height to auto
canvas_preview.oncontextmenu = () => false;

const simple_coordinates_canvas_width = 300;
canvas_simple_coordinates.style.width = `${simple_coordinates_canvas_width}px`;
canvas_simple_coordinates.style.height = 'auto'; // set height to auto
canvas_simple_coordinates.oncontextmenu = () => false;

const result_canvas_width = 800;
canvas_results.style.width = `${result_canvas_width}px`;
canvas_results.style.height = 'auto'; // set height to auto
canvas_results.oncontextmenu = () => false;

// default text for the blueprint
text_blueprint.textContent = 'No blueprint available. Please run the solver first.';

// -----------------------------------------------
// link element to callbacks
// -----------------------------------------------
canvas_preview.addEventListener('mousedown', callback_canvas_clicks);
button_submit_image.addEventListener('click', callback_submit_image);
button_run_solver.addEventListener('click', callback_run_solver);
button_copy_blueprint.addEventListener('click', callback_copy_blueprint);

// -----------------------------------------------
// callback functions and helpers
// -----------------------------------------------
function update_canvas_image(canvas, image_url) 
{
    const canvas_context = canvas.getContext('2d');

    const img = new Image();
    img.onload = function() 
    {
        // clear canvas
        canvas_context.clearRect(0, 0, canvas.width, canvas.height); 

        // set canvas size to image size
        canvas.width = img.width;
        canvas.height = img.height;

        // draw image on the canvas
        canvas_context.drawImage(img, 0, 0, canvas.width, canvas.height); 
        
        // free the object URL
        URL.revokeObjectURL(image_url);
    };
    img.src = image_url; // set image source to the URL
}


async function callback_submit_image() 
{
    // ----------------------------------------------------
    // local processing
    // ----------------------------------------------------

    // check file input
    if (button_upload_file.files.length === 0) 
    {
        console.error('Please upload a file first.');
        return;
    }

    // reset clicks
    leftClicks = [];
    rightClicks = [];

    // show the file in the convas
    const file = button_upload_file.files[0];
    const reader = new FileReader();
    reader.onload = function(event)
    {
        update_canvas_image(canvas_preview, event.target.result); // update canvas with the image
    };
    reader.readAsDataURL(file); // read file as data URL

    // ----------------------------------------------------
    // send data
    // ----------------------------------------------------
    
    // send file to server and get task_id
    const form = new FormData();
    form.append('file', file);
    const response = await fetch('/add_task/', {method: 'POST', body: form});
    
    // ----------------------------------------------------
    // process response
    // ----------------------------------------------------

    // ensure the response is ok
    if (!response.ok)
    {
        console.error('Failed to upload file:', response.statusText);
        return;
    }

    // get the task_id from the response
    const data = await response.json();
    task_id = data.task_id;
}

async function callback_canvas_clicks(event) 
{                        
    // ----------------------------------------------------
    // local processing
    // ----------------------------------------------------
    
    // won't work if no task_id
    if (!task_id)
    {
        console.error('No task_id available. Please upload a file first.');
        return;
    }

    // compute position
    const preview_canvas_rectangle = canvas_preview.getBoundingClientRect(); // update the rectangle entity every time
    const screen_x = event.clientX;
    const screen_y = event.clientY;
    const rect_x = screen_x - preview_canvas_rectangle.left; // relative to canvas rectange
    const rect_y = screen_y - preview_canvas_rectangle.top; // relative to canvas rectange
    const canvas_x = rect_x * (canvas_preview.width / preview_canvas_rectangle.width);
    const canvas_y = rect_y * (canvas_preview.height / preview_canvas_rectangle.height);
    const int_canvas_x = Math.round(canvas_x);
    const int_canvas_y = Math.round(canvas_y);

    // get left or right click
    const left = event.button === 0;

    // --- log ---
    console.log(`${left? 'Left' : 'Right'} click at (${int_canvas_x}, ${int_canvas_y}) on task_id: ${task_id}`);
    // -----------


    // ----------------------------------------------------
    // send data
    // ----------------------------------------------------

    // create a form with the click data
    const form = new FormData();
    form.append('task_id', task_id); // add task_id to the form
    form.append('x', int_canvas_x.toString());
    form.append('y', int_canvas_y.toString());
    form.append('left', left ? 'true' : 'false');
    const response = await fetch('/send_clicks/', {method: 'POST', body: form});

    // ----------------------------------------------------
    // process response
    // ----------------------------------------------------

    // ensure the response is ok
    if (!response.ok) 
    {
        console.error('Failed to send click data:', response.statusText);
        return;
    }
    
    // // read zip
    // const zipBlob = await response.blob();
    // const zip = await JSZip.loadAsync(zipBlob);

    // // Draw preview if it exists
    // if (zip.files["preview.png"]) 
    // {
    //     const previewImage = await zip.files["preview.png"].async("blob");
    //     const previewImageUrl = URL.createObjectURL(previewImage);
    //     update_canvas_image(preview_canvas, previewImageUrl);
    // } 

    // // Draw simple coordinates if it exists
    // if (zip.files["coordinates.png"]) 
    // {
    //     const coordinatesImage = await zip.files["coordinates.png"].async("blob");
    //     const coordinatesImageUrl = URL.createObjectURL(coordinatesImage);
    //     update_canvas_image(simple_coordinates_canvas, coordinatesImageUrl);
    // } 

    // decode image
    const data = await response.json();
    const preview_image_base64 = data.preview_image;
    const simple_coordinates_image_base64 = data.simple_coordinate_image;
    
    if (preview_image_base64) 
    {
        const previewImageUrl = `data:image/png;base64,${preview_image_base64}`;
        update_canvas_image(canvas_preview, previewImageUrl);
    } 
    
    if (simple_coordinates_image_base64) 
    {
        const coordinatesImageUrl = `data:image/png;base64,${simple_coordinates_image_base64}`;
        update_canvas_image(canvas_simple_coordinates, coordinatesImageUrl);
    }
}

async function callback_run_solver() 
{
    // ----------------------------------------------------
    // local processing
    // ----------------------------------------------------

    // won't work if no task_id
    if (!task_id) 
    {
        console.error('No task_id available. Please upload a file first.');
        return;
    }

    // ----------------------------------------------------
    // send data
    // ----------------------------------------------------

    // send request to run optimizer
    const form = new FormData();
    form.append('task_id', task_id); // add task_id to the form
    const response = await fetch(`/run_solver/`, {method: 'POST', body: form});

    // ----------------------------------------------------
    // process response
    // ----------------------------------------------------

    // ensure the response is ok
    if (!response.ok) 
    {
        console.error('Failed to run optimizer:', response.statusText);
        return;
    }

    // result is a file and a string
    const result = await response.json();

    // draw the image on the canvas
    update_canvas_image(canvas_results, `data:image/png;base64,${result.solution_image}`);

    // show result in the pre named blueprint
    text_blueprint.textContent = result.blueprint;
}

function callback_copy_blueprint() 
{
    // ----------------------------------------------------
    // local processing
    // ----------------------------------------------------

    // won't work if no blueprint
    if (!text_blueprint.textContent) 
    {
        console.error('No blueprint available to copy.');
        return;
    }

    // copy the blueprint to clipboard
    navigator.clipboard.writeText(text_blueprint.textContent)
        .then(() => {
            console.log('Blueprint copied to clipboard successfully!');
        })
        .catch(err => {
            console.error('Failed to copy blueprint:', err);
        });
}
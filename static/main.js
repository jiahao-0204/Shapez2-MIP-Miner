// -----------------------------------------------
// data
// -----------------------------------------------
let leftClicks = [];
let rightClicks = [];
let task_id = null;
const default_threshold = 0.4;
let threshold = default_threshold;

// -----------------------------------------------
// get web page elements
// -----------------------------------------------
const button_choose_file = document.getElementById('choose_file'); 
const button_upload_file = document.getElementById('upload_file');
const canvas_preview = document.getElementById('preview_canvas');
const canvas_simple_coordinates = document.getElementById('simple_coordinates_canvas');
const canvas_results = document.getElementById('result_canvas');

const button_use_default_blueprint = document.getElementById('use_default_blueprint');
const text_miner_blueprint = document.getElementById('miner_blueprint');
const button_generate_blueprint = document.getElementById('generate_blueprint');
const button_copy_blueprint = document.getElementById('copy_blueprint');
const text_blueprint = document.getElementById('blueprint_text');

const button_run_solver_and_stream = document.getElementById('run_solver_and_stream');
const text_solver_output = document.getElementById("solver_output");

const input_threshold = document.getElementById('input_threshold');
const button_decrease_threshold = document.getElementById('decrease_threshold');
const button_increase_threshold = document.getElementById('increase_threshold');

// -----------------------------------------------
// setup elements
// -----------------------------------------------
canvas_preview.oncontextmenu = () => false;
callback_use_default_blueprint();
input_threshold.value = threshold.toFixed(2); // set initial value in the input field

// -----------------------------------------------
// link element to callbacks
// -----------------------------------------------
canvas_preview.addEventListener('mousedown', callback_canvas_clicks);
button_upload_file.addEventListener('click', callback_upload_file);
button_copy_blueprint.addEventListener('click', callback_copy_blueprint);
input_threshold.addEventListener('change', callback_threshold_change);
button_decrease_threshold.addEventListener('click', callback_decrease_threshold);
button_increase_threshold.addEventListener('click', callback_increase_threshold);
button_run_solver_and_stream.addEventListener('click', callback_run_solver_and_stream);
button_use_default_blueprint.addEventListener('click', callback_use_default_blueprint);
button_generate_blueprint.addEventListener('click', callback_generate_blueprint);

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


async function callback_upload_file() 
{
    // upload file and get back task_id

    // ----------------------------------------------------
    // local processing
    // ----------------------------------------------------

    // check file input
    if (button_choose_file.files.length === 0) 
    {
        console.error('Please upload a file first.');
        return;
    }

    // reset clicks
    leftClicks = [];
    rightClicks = [];

    // show the file in the convas
    const file = button_choose_file.files[0];
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

async function update_preview()
{
    // ----------------------------------------------------
    // local processing
    // ----------------------------------------------------

    // request update from server
    if (!task_id)
    {
        console.error('No task_id available. Please upload a file first.');
        return;
    }

    // ----------------------------------------------------
    // send data
    // ----------------------------------------------------
    form = new FormData();
    form.append('task_id', task_id); // add task_id to the form
    form.append('threshold', threshold.toString()); // add threshold to the form
    const response = await fetch(`/update_preview/`, {method: 'POST', body: form});

    // ----------------------------------------------------
    // process response
    // ----------------------------------------------------

    // decode image
    const data = await response.json();
    const current_threshold = data.current_threshold;
    const preview_image_base64 = data.preview_image;
    const simple_coordinates_image_base64 = data.simple_coordinate_image;
    
    threshold = current_threshold; // update the threshold value
    input_threshold.value = threshold.toFixed(2); // update the input field

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

    update_preview()
}

async function callback_threshold_change()
{
    // set threshold value from input
    threshold = parseFloat(input_threshold.value);

    if (isNaN(threshold)) 
    {
        threshold = default_threshold; // reset to default if input is not a number
        input_threshold.value = threshold.toFixed(2); // update the input field
    }

    update_preview()
}

async function callback_decrease_threshold()
{
    threshold -= 0.05; // decrease threshold by 0.01
    input_threshold.value = threshold.toFixed(2); // update the input field
    callback_threshold_change(); // call the threshold change callback to update the preview
}

async function callback_increase_threshold()
{
    threshold += 0.05; // increase threshold by 0.01
    input_threshold.value = threshold.toFixed(2); // update the input field
    callback_threshold_change(); // call the threshold change callback to update the preview
}   

function callback_run_solver_and_stream() 
{
    // ----------------------------------------------------
    // local processing
    // ----------------------------------------------------

    // clear output
    text_solver_output.textContent = "";

    // get event source for streaming logs
    const eventSource = new EventSource(`/run_solver_and_stream/${task_id}`);

    // upon message
    eventSource.onmessage = async function(event) 
    {
        const line = event.data;
        text_solver_output.textContent += line + "\n";
        text_solver_output.scrollTop = text_solver_output.scrollHeight;

        // when done
        if (line === "DONE") 
        {
            eventSource.close();

            try 
            {
                // -------------------------------------
                // send to server
                // -------------------------------------

                // request the final result
                const response = await fetch(`/get_solver_results/${task_id}`);
                
                // -------------------------------------
                // process response
                // -------------------------------------

                // ensure the response is ok
                if (!response.ok) 
                {
                    console.error('Failed to get final result:', response.statusText);
                    return;
                }

                // get the final result
                const result = await response.json();

                // draw the image on the canvas
                update_canvas_image(canvas_results, `data:image/png;base64,${result.solution_image}`);

                // try generating the blueprint
                callback_generate_blueprint();
            } 
            catch (err) 
            {
                console.error("Error fetching final result:", err);
            }
        }
    };

    // upon error
    eventSource.onerror = function() 
    {
        text_solver_output.textContent += "\n[Connection closed or error]\n";
        eventSource.close();
    };
}

function callback_use_default_blueprint()
{
    text_miner_blueprint.value = 'SHAPEZ2-3-H4sIAAPgQGgA/6yXUWujQBSF/8tlH33IaKKOj6FdCCQQ2hK6LGEZ6qQ7YMdyHemG4H9fbZrgbppEj0VQxPvNnZlzj5fZ0YoSIXzfo+mSkh19c9tXTQnNikzZlDyaPeW2+XCjnKLkJ5n6PVlmym1yfinIs2WW7W9U/FavOrkr9xetK49urWOjixrc0UM97Fxt89L9um8iF8ZqrjNM23mnpclSY5+/NPMjJaFHPyiZeHRXr9d7n8vtH8fqyeV8ozeqzNzMOs1WZSvFRllHlfdORjAZw6SESSFw1MfRAEfHQ9HmUbMBMmOM9QewAmcljsY4GuFoOHifwnZZTHXmPqi53lxRJ9wzC83Pmv2HXMwvV0L3+HHP+Ek7vrWG7zm/KU7PYeEZ7JOlLwxzzjr9j43ObF6nxDGw89GBPDDLnN29tqnmK3YI2iXSc7H+cYjLgpyAAQqOUXDyD9hXEhH0UuMD8s9sbbeUYoAw0XGIzvUQDi6HCNQmBjn5yYyv/xTkEG3kZWk6waMBuo6OQ/QrKQFyPsgFIDcGuQnIhSAXnXAd/QV01ahf04v7hcvTafV1INbs5MVe14WVQJ8cHUjEPxKzj8TcIzHzSMw7ErOOxJwjOxlnXZ9QjVW8XWkuTHMkbc7LVbWuqr8CDABeAPEsPg8AAA==$'
}

async function callback_generate_blueprint()
{
    // ----------------------------------------------------
    // local processing
    // ----------------------------------------------------

    // request the blueprint from the server
    if (!task_id)
    {
        console.error('No task_id available. Please upload a file first.');
        return;
    }

    // ----------------------------------------------------
    // send data
    // ----------------------------------------------------
    form = new FormData();
    form.append('task_id', task_id); // add task_id to the form
    form.append('miner_blueprint', text_miner_blueprint.value); // add miner blueprint to the form
    const response = await fetch(`/generate_blueprint/`, {method: 'POST', body: form});

    // ----------------------------------------------------
    // process response
    // ----------------------------------------------------
    // ensure the response is ok
    if (!response.ok)
    {
        console.error('Failed to generate blueprint:', response.statusText);
        return;
    }

    // get the blueprint text
    const data = await response.json();
    const blueprint = data.blueprint;

    // show the blueprint in the text area
    text_blueprint.textContent = blueprint;
    console.log('Blueprint generated successfully!');
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
// -----------------------------------------------
// data
// -----------------------------------------------
let leftClicks = [];
let rightClicks = [];
let task_id = null;
const default_threshold = 0.4;
let threshold = default_threshold;

const brush_blueprint = "SHAPEZ2-3-H4sIAHZLR2gC/53SzUrDQBRA4Vcpg0sF753/LkUXBYVSXShSJGjEQExKkwql9N2dal247CGQGe7kTDbfznyZ6URE9XxiruZlvzNn43ZVl52ZDW3VvZlyMnvtu5+z62qsyubZNGUynbfV+N6vP4fyTbdp27+3GT6qVT1dbH4fs9yX2U03rpt6ONQ781iWyzJ8Oq6L4/pw+O9tte0348v94ZK7pqvXpvT/mwshkZLIksiRyJMokCiSKJEonxAJACEEhBAQQkAIASEEhBAQQkAIASEEhAIQSkAoAaEEhBIQSkAoAaEEhBIQSkBYAMISEJaAsASEJSAsAWEJCEtAWALCEhAOgHAEhCMgHAHhCAhHQDgCwhEQjoBwBIQHIDwB4QkIT0B4AsITEJ6A8ASEJyA8AREAiEBABAIiEBCBgAgERCAgAgERCIhAQEQAIhIQkYCIBEQkICIBEQmISEBEAiISEAmASAREIiASAZEIiERAJAIiERCJgEgERAYgMgGRCYhMQGQCIhMQmYDIBEQmIPIpIJb7/TeqFG9MIRUAAA==$"

// -----------------------------------------------
// get web page elements
// -----------------------------------------------
const button_copy_brush_blueprint = document.getElementById('copy_brush_blueprint');
button_copy_brush_blueprint.addEventListener('click', () => {
    // copy the brush blueprint to clipboard
    navigator.clipboard.writeText(brush_blueprint)
        .then(() => {
            console.log('Brush blueprint copied to clipboard successfully!');
        })
        .catch(err => {
            console.error('Failed to copy brush blueprint:', err);
        });
}
);

const input_miner_blueprint = document.getElementById('input_miner_blueprint');
input_miner_blueprint.addEventListener('change', async function() 
{
    // send the blueprint to the server which returns the simple coordinate preview
    const input_blueprint = input_miner_blueprint.value;
    
    // skip if empty
    if (!input_blueprint.trim()) {
        console.error('Blueprint is empty. Please enter a valid blueprint.');
        return;
    }

    // send to fastapi
    form = new FormData();
    form.append('input_blueprint', input_blueprint); // add miner blueprint to the form
    const response = await fetch(`/get_simple_coordinates_preview/`, {method: 'POST', body: form});

    // ensure the response is ok
    if (!response.ok) {
        const error_text = await response.text();
        console.error('Failed to get simple coordinates preview:', error_text);
        task_not_found_alert(error_text);
        return;
    }

    // get the simple coordinates image
    const data = await response.json();
    const simple_coordinates_image_base64 = data.simple_coordinates_image;
    if (simple_coordinates_image_base64) {
        const coordinatesImageUrl = `data:image/png;base64,${simple_coordinates_image_base64}`;
        update_canvas_image(canvas_simple_coordinates, coordinatesImageUrl);
    } else {
        console.error('No simple coordinates image returned from the server.');
    }

});

const canvas_simple_coordinates = document.getElementById('simple_coordinates_canvas');

const checkbox_with_elevator = document.getElementById('with_elevator');
const input_miner_timelimit = document.getElementById('miner_timelimit');
const input_miner_threshold = document.getElementById('miner_threshold');
const belt_miner_timelimit = document.getElementById('belt_timelimit');
const belt_miner_threshold = document.getElementById('belt_threshold');
const button_run_solver_and_stream = document.getElementById('run_solver_and_stream');
const text_solver_output = document.getElementById("solver_output");

const canvas_results = document.getElementById('result_canvas');
const button_use_default_blueprint = document.getElementById('use_default_blueprint');
const text_miner_blueprint = document.getElementById('miner_blueprint');
const button_generate_blueprint = document.getElementById('generate_blueprint');
const button_copy_blueprint = document.getElementById('copy_blueprint');
const text_blueprint = document.getElementById('blueprint_text');

// -----------------------------------------------
// setup elements
// -----------------------------------------------
callback_use_default_blueprint();

// -----------------------------------------------
// link element to callbacks
// -----------------------------------------------
button_copy_blueprint.addEventListener('click', callback_copy_blueprint);
input_miner_timelimit.addEventListener('change', () => {
    const value = input_miner_timelimit.value;
    if (value) {
        // cap between 0 and 120
        const cappedValue = Math.max(0, Math.min(120, parseFloat(value)));
        input_miner_timelimit.value = cappedValue.toFixed(2);
    }
});
input_miner_threshold.addEventListener('change', () => {
    const value = input_miner_threshold.value;
    if (value) {
        // cap between 0 and 100
        const cappedValue = Math.max(0, Math.min(100, parseFloat(value)));
        input_miner_threshold.value = cappedValue.toFixed(2);
    }
});
belt_miner_timelimit.addEventListener('change', () => {
    const value = belt_miner_timelimit.value;
    if (value) {
        // cap between 0 and 120
        const cappedValue = Math.max(0, Math.min(120, parseFloat(value)));
        belt_miner_timelimit.value = cappedValue.toFixed(2);
    }
});
belt_miner_threshold.addEventListener('change', () => {
    const value = belt_miner_threshold.value;
    if (value) {
        // cap between 0 and 100
        const cappedValue = Math.max(0, Math.min(100, parseFloat(value)));
        belt_miner_threshold.value = cappedValue.toFixed(2);
    }
});

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

function task_not_found_alert(error_text) 
{
    if (error_text.includes("Task not found")) 
    {
        alert("Task not found (Server delete tasks after 10 minutes). Please refresh or try again.");
    }
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
        const errorText = await response.text();
        console.error("Failed to upload file:", errorText);
        task_not_found_alert(error_text);
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

    if (!response.ok)
    {
        const error_text = await response.text();
        console.error("Failed to update preview:", error_text);
        task_not_found_alert(error_text);
        return;
    }

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
        const error_text = await response.text();
        console.error('Failed to send click data:', error_text);
        task_not_found_alert(error_text);
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

    // cap between 0 and 1
    threshold = Math.max(0, Math.min(1, threshold));
    input_threshold.value = threshold.toFixed(2); // update the input field

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

async function callback_run_solver_and_stream() 
{
    // ----------------------------------------------------
    // local processing
    // ----------------------------------------------------

    // check input miner blueprint
    if (!input_miner_blueprint.value.trim()) {
        console.error('Blueprint is empty. Please enter a valid blueprint.');
        return;
    }

    // send request to server for task_id
    const response = await fetch('/get_task_id/', {method: 'GET'});
    // ensure the response is ok
    if (!response.ok) 
    {
        const error_text = await response.text();
        console.error('Failed to get task_id:', error_text);
        task_not_found_alert(error_text);
        return;
    }

    // get the task_id from the response
    const data = await response.json();
    task_id = data.task_id;
    if (!task_id) 
    {
        console.error('No task_id received from the server.');
        return;
    }
    console.log('Task ID:', task_id);

    // clear output
    text_solver_output.textContent = "";

    // get elevator checkbox value
    const with_elevator_bool = checkbox_with_elevator.checked.toString();
    console.log('With elevator:', with_elevator_bool);
    
    // get event source for streaming logs
    const params = new URLSearchParams(
    {
        task_id: task_id,
        with_elevator_bool: with_elevator_bool,
        miner_time: input_miner_timelimit.value,
        miner_threshold: input_miner_threshold.value,
        belt_time: belt_miner_timelimit.value,
        belt_threshold: belt_miner_threshold.value,
        input_miner_blueprint: input_miner_blueprint.value,
    });
    const eventSource = new EventSource(`/run_solver_and_stream?${params.toString()}`);

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
                    const error_text = await response.text();
                    console.error('Failed to get final result:', error_text);
                    task_not_found_alert(error_text);
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
    text_miner_blueprint.value = 'SHAPEZ2-2-H4sIAN0dd2cA/6xaXW+bMBT9L9Ye0YTNl0Haw7J2UrVEqtqs2jRVE0qcDo1C5JBtUZX/PhIMNRCofU37ELXhnHt8fX2uDbygBxRhbHsWmt2i6AW9Kw5bhiJ0s0vjbI0sdLPKs9MXV3ERo+gHSsq/o+rb2zResWeWFeVl53+n8SHfF+/n54+f97/iLVskGePIyvZpKi66ft4WB/R4tNB1VvCE7UrWF7QsY17AoZksarZP0nWSPQ3JKgUVm5w/70TAKuruxBfd7avfXuRvKPIt9B1FZQ7uUORYZy3X/woer4qcX7FNvE+Lm6xgPIvTh5gncTnio3VGBmAklZBYCxmCkZVaV1Y7Y2khQHO26QIXCec5Z+uawO8TzJNNgb9uFcBN9HmjW4r+Oed/Y74ezRYMizF4kgRUccA9sbXM25wX9yxbM95FWOhTec2Xj+efD01Y5xLDHVux5M8QRwl/xRNwiYjQIKgLz7MrD3jB+BPjZJnj+Rslhb1uotRrWWBbI9WsR38Aq7wYKgKiGdwfxY4UpqgLA9liQcB0Y9sAHPalD9dJp5p90BxXEQOD+jiFV7XadmEIJKwyBsEqE2ybxA8vDFt9NQs0GUia0tBdcFsEQakMdQBtHAQVgj31ddzJUgv5dkN7jQdu3UCw8BvQ3NRYxcF2q/FVt2Eb71Jo93FQjdTBXXg7hmXdbQ1awaO9XpYUOpl3YXTqVUXA9lwXFcwf60lxYLK9AYPULkxPam0OuDq9CQbT2gxUxbI8HwDHywuy+XEN+rlQS1smMotXv8cwbo2pjA8oOJTwGLBGQpjx+ibgRjlcM1AtRCeVdd5v06Qor8bL3BlfxVSe0lNJkNEmKlBVRgkgNW4bD6lfINg3ARNp2RG4ZwXDNBqW5Yx6gPIdkEDzGEJk4zZOwmUe7SwMbrTf3j8S2AZfoLHBBp+C7Nsf9SOlg4Wt3KICeZRYp2METajG8R34zYVasoKjBVJ+nJah6SiGm1otVXsrZMOsTB/ndqYGqhbeiqFotzNFBsqJkXICOzja5gcwG+qUdCDzBkL6REA5ZCo54D4SNizgu2sYq+/8bbn3aPlqDcWmxioRqe4VbTlJWt7aVg0xV9xSC6oU/yKFxl4Dd1I/gRKTJdTWQ6bSA9+LBfLBUkXI4qkjJOiefYAMOk47RIGNKahuoQznYxIeffMfyc0kRFS3dEczRKbKEJkqQwZEocEZITQ4IwirvnCrRqtBUcnpTfpTaw2pN6mg3x7P8q/yv5nyAIBNiho7MTVsCXSiDkUnaVB0ov5EDduT3X7xAvxM0O0vDYU9X/Oqy8gdUMXHxoYMgQFDvZHzjLPYonA004jd0e2v6pNdUwpiToHNKWxjitCYoeUUo9P4aKFZksX88MD4Ljm9+XZ6Z+94fDwe/wsgwABYhMLTwicAAA==$'
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

    const miner_blueprint_value = input_miner_blueprint.value;
    if (miner_blueprint_value === "") 
    {
        miner_blueprint_value = "empty"; 
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
        const error_text = await response.text();
        console.error('Failed to generate blueprint:', error_text);
        task_not_found_alert(error_text);
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
// -----------------------------------------------
// data
// -----------------------------------------------
let leftClicks = [];
let rightClicks = [];
let task_id = null;
const default_threshold = 0.4;
let threshold = default_threshold;

const brush_blueprint = "SHAPEZ2-3-H4sIAHZLR2gC/53SzUrDQBRA4Vcpg0sF753/LkUXBYVSXShSJGjEQExKkwql9N2dal247CGQGe7kTDbfznyZ6URE9XxiruZlvzNn43ZVl52ZDW3VvZlyMnvtu5+z62qsyubZNGUynbfV+N6vP4fyTbdp27+3GT6qVT1dbH4fs9yX2U03rpt6ONQ781iWyzJ8Oq6L4/pw+O9tte0348v94ZK7pqvXpvT/mwshkZLIksiRyJMokCiSKJEonxAJACEEhBAQQkAIASEEhBAQQkAIASEEhAIQSkAoAaEEhBIQSkAoAaEEhBIQSkBYAMISEJaAsASEJSAsAWEJCEtAWALCEhAOgHAEhCMgHAHhCAhHQDgCwhEQjoBwBIQHIDwB4QkIT0B4AsITEJ6A8ASEJyA8AREAiEBABAIiEBCBgAgERCAgAgERCIhAQEQAIhIQkYCIBEQkICIBEQmISEBEAiISEAmASAREIiASAZEIiERAJAIiERCJgEgERAYgMgGRCYhMQGQCIhMQmYDIBEQmIPIpIJb7/TeqFG9MIRUAAA==$"
const brush_fluid_blueprint = "SHAPEZ2-3-H4sIANS0SmgA/4yWTUvDQBCG/8vgcecwG3PZo6hQUCgiokiRxUYMxKTk41BC/ruRXjxlHgqB0Dez7zzvsMwsL5LMYgxys5c0y9V4PlWSZDc0uT1KkN1n1/79cZvHLOld6vU97Zs8fnX9zyChnZrm8pDhO5+q9DRdfnJYgty1Y19Xw/rhLK+S9DrIm6T1+bye8ZDP3TR+3DdTfXys26qXJfyXFUwWmcyAjNRRgzroS2Gb2F/p6QoWQsFCKFgIBQsBHqcGddAXPhdS80OILITIQogshMhCgHXUoI7Wg20qpOaHYCwEYyEYC8FYCMbqYB30pbBNhdS2Q/Doe9g93h7ozS+30bpMXZguRTLDbITZBLMBZvNrqIpCGfOkrEFltFz07ApnNzi7wNn9zaqoMRmsxhpURstFz1YYtsGwBYbtL+wsNSZjnhQeymi56NkKzzZ4tsCz/Z05UmMy5klZgwq9eehLhL5E6EuEvkTomW81JmOelDWojNYG+sOy/AogwAAP2KUlJg8AAA==$"

const default_miner_blueprint = "SHAPEZ2-3-H4sIALPpUWgA/6yYXYvaQBSG/8vQy1w4E/NhLsNuQYggaqWlSBl03A5NExnHtiL5701MdBOTmjknZWFB1mff8/lmJheyJgGljFkknJPgQj7o80GQgEyPMU92xCLTbZoUf3jhmpPgK5H552Aec71P1c8jsZJTHJe/yPE7P4hgcSp/yCazyGuilRTHHLyQVf5vI35OT/rbsvjmTCZC5QphXTc8yXgnk7f/qvw5z3FskS8kcCyyyD9Y12Be/2jFtzpVL2LPT7GeJlqohMdrriRPNMmsEmVD0UI8Z20Q6+NRF49S78r6JRSKWM9TpZci2Qn1HJnAETpCMBTO5NlE99YBc8KBRWZIkmLJMkuGzZKhs2ToLEEkra0hgw01rS8EjJ3cUYjgqGMDZ0K9CbW6et9TMQej1bAnAykfbWou3g5tvDF5Q1UxqDfASMdDrd+tB2y0IlW4dl3SCHSRgu59mdvgQmyF/NWHtmKtKvMxVb+52j2HmfG0V93AltTvqmhPgmUTPbBWK0ajinh1NYOCeI0KmhmwPSC+6iTkgUpYQfCu3YwGvgnUbT74O1ONxF6b8AxaJNrZFbMqIVepenxgJrxCzYeuyg+yE5UGcuhG6DEYD6mpPwSeoDcTODc+3rx9sP+y+4ERLHZjWfswxVYpjXowCn1INNOyc4me72MqWPnE+z2hc1I6jGYmlUqV2D32HmSPTidjFvIEbYpV93Fpuo2Ql4dY6hygq9TuEWU463DbN0dzUa/d1UjuNf10CPn2h6ksQ1TarvUI6Ob2LfTHe0TXlv1jDH3osvmN6vT0xOm+zZs11Gkst5ng+whFyJGn7UkwGSOnTTcDN1kZ5+GSPnT3RrhDjfv40AcoO5hTo1s70VBozf16sQ177bSNsWgT62zTY1XtDszMJaq5ZLhzn/vwIgY+HRuLhDLh6rwW6iiLl7XFm+Qs22TZXwEGADQ+codYFgAA$"
const default_miner_blueprint_text = "Use default blueprint (1:12 Balanced Shape Miner 95 Bulidings by Hybrid)"

const default_fluid_miner_blueprint = "SHAPEZ2-3-H4sIADa2SmgA/6yXYWvqMBSG/8vhfuwHk6qt/ejdBg4HsnuvbAwZwcYtrEtLmnIR6X9fa52Lc6s9xyFYinl83+Q9JyEbmEPEGOcejGcQbeCXXWcSIpjkidAxeDBZprr+4UJYAdEDqOo9miXCrlLzmoOniyRpviB/FpmMbovmA4vSg0ttjZJ5BW7gb/W3U7FOC/t4lRQqvlFamkph7OqOC5XESj/9qPJdPUcP7iEaeHBbvXhbM7PiNbuQK1EkdqKtNFokc2GU0BZKr6E4ifJJVP8Mqn5UmI+0iMY4DWNnYYwUGhrzaVj/HCwkxRaSUgtJq4+lBlsq2I1XmbxKzX9h4vbxtcWOwPBdwLFVUVO5su2Iq3F6dPgx+LrQS6tS/R0QuMB2a5ulxv6ROpamXWSEFRkRRFgPq/JOdJQJ9h2A99a0jZPMb5Pm+YliOYL+ZWOxfGmrmg+P032Xop026GHddS4OtO4+carjnovi0kdLDg6nSYunwTk9HX6wCZ/o8+ATia/4Hhkd0Wd6INol1eGxYncs/HpdMZqMpsmwms15NcSUAHcQRE/7NIw5JxfHGAywS+HTsL4zL47Fjk7k1p2c7Y9kbFo7Bh0Xntt59PGB7Rh0Yniu/43HjtzR+n8d2qK6pSktzHouTa7qa1l9ZyzLRVm+CSDAAAoWop9CDgAA$"
const default_fluid_miner_blueprint_text = "Use default blueprint (Fluid Miner)"

const miner_timelimit_max = 300;
const saturation_timelimit_max = 300;

const stats_refresh_interval_in_seconds = 5; // seconds

let solve_for_fluid = false;

// -----------------------------------------------
// get web page elements
// -----------------------------------------------
// stats element
const stats_tasks_ran_in_total = document.getElementById('stats_tasks_ran_in_total');
const stats_tasks_ran_today = document.getElementById('stats_tasks_ran_today');
const stats_current_running_tasks_num = document.getElementById('stats_current_running_tasks_num');

const button_copy_brush_blueprint = document.getElementById('copy_brush_blueprint');
button_copy_brush_blueprint.addEventListener('click', () => {
    // copy the brush blueprint to clipboard
    if (solve_for_fluid)
    {
        navigator.clipboard.writeText(brush_fluid_blueprint)
            .then(() => {
                console.log('Brush blueprint copied to clipboard successfully!');
            })
            .catch(err => {
                console.error('Failed to copy brush blueprint:', err);
            });
    }
    else
    {
        navigator.clipboard.writeText(brush_blueprint)
            .then(() => {
                console.log('Brush blueprint copied to clipboard successfully!');
            })
            .catch(err => {
                console.error('Failed to copy brush blueprint:', err);
            });
    }
});

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
const miners_timelimit = document.getElementById('miners_timelimit');
const saturation_timelimit = document.getElementById('saturation_timelimit');
const button_run_solver_and_stream = document.getElementById('run_solver_and_stream');
const text_solver_output = document.getElementById("solver_output");

const canvas_results = document.getElementById('result_canvas');
const button_use_default_blueprint = document.getElementById('use_default_blueprint');
const text_miner_blueprint = document.getElementById('miner_blueprint');
const button_generate_blueprint = document.getElementById('generate_blueprint');
const button_copy_blueprint = document.getElementById('copy_blueprint');
const text_blueprint = document.getElementById('blueprint_text');

const checkbox_solve_for_fluid = document.getElementById('solve_for_fluid');
checkbox_solve_for_fluid.addEventListener('click', () => {
    solve_for_fluid = checkbox_solve_for_fluid.checked;
    update_use_default_blueprint_text();
    callback_use_default_blueprint();
});

const checkbox_remove_non_saturated_miners = document.getElementById('remove_non_saturated_miners');
checkbox_remove_non_saturated_miners.addEventListener('change', () => {
    // if have task id, update solver result
    if (task_id) {
        get_solver_result();
    }
});

// -----------------------------------------------
// setup elements
// -----------------------------------------------
update_use_default_blueprint_text();
callback_use_default_blueprint();

// pull once at start
function pull_stats_once()
{
    fetch('/get_stats/')
    .then(response => response.json())
    .then(data => {
        stats_tasks_ran_in_total.textContent = data.tasks_ran_in_total;
        stats_tasks_ran_today.textContent = data.tasks_ran_today;
        stats_current_running_tasks_num.textContent = data.current_running_tasks_num;
    })
    .catch(error => console.error('Error fetching stats:', error));
}

// pull every 5 seconds
function pull_stats_periodically()
{
    setInterval(() => pull_stats_once(), stats_refresh_interval_in_seconds * 1000);
}

pull_stats_once();
pull_stats_periodically();

// -----------------------------------------------
// link element to callbacks
// -----------------------------------------------
button_copy_blueprint.addEventListener('click', callback_copy_blueprint);
miners_timelimit.addEventListener('change', () => {
    const value = miners_timelimit.value;
    if (value) {
        // cap between 0 and miner_timelimit_max
        const cappedValue = Math.max(0, Math.min(miner_timelimit_max, parseFloat(value)));
        miners_timelimit.value = cappedValue.toFixed(2);
    }
});
saturation_timelimit.addEventListener('change', () => {
    const value = saturation_timelimit.value;
    if (value) {
        // cap between 0 and saturation_timelimit_max
        const cappedValue = Math.max(0, Math.min(saturation_timelimit_max, parseFloat(value)));
        saturation_timelimit.value = cappedValue.toFixed(2);
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

async function get_solver_result()
{
    // -------------------------------------
    // send to server
    // -------------------------------------

    // request the final result
    form = new FormData();
    form.append('task_id', task_id); // add task_id to the form
    form.append('remove_non_saturated_miners', checkbox_remove_non_saturated_miners.checked.toString()); // add remove_non_saturated_miners to the form
    const response = await fetch(`/get_solver_results`, {method: 'POST', body: form});
    
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
        miners_timelimit: miners_timelimit.value,
        saturation_timelimit: saturation_timelimit.value,
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
                get_solver_result();
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

function update_use_default_blueprint_text()
{
    if (solve_for_fluid)
    {
        button_use_default_blueprint.textContent = default_fluid_miner_blueprint_text;
    }
    else
    {
        button_use_default_blueprint.textContent = default_miner_blueprint_text;
    }
}

function callback_use_default_blueprint()
{
    if (solve_for_fluid)
    {
        text_miner_blueprint.value = default_fluid_miner_blueprint; // set default blueprint
    }
    else
    {
        text_miner_blueprint.value = default_miner_blueprint; // set default blueprint
    }
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
    if (miner_blueprint_value == "" || miner_blueprint_value == null) 
    {
        miner_blueprint_value = "empty"; 
    }

    // ----------------------------------------------------
    // send data
    // ----------------------------------------------------
    form = new FormData();
    form.append('task_id', task_id); // add task_id to the form
    form.append('miner_blueprint', text_miner_blueprint.value); // add miner blueprint to the form
    form.append('solve_for_fluid', solve_for_fluid); // add solve for fluid to the form
    form.append('remove_non_saturated_miners', checkbox_remove_non_saturated_miners.checked); // add remove non-saturated miners to the form
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
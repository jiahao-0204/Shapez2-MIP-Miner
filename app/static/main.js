// -----------------------------------------------
// data
// -----------------------------------------------
let leftClicks = [];
let rightClicks = [];
let task_id = null;
const default_threshold = 0.4;
let threshold = default_threshold;

const brush_blueprint = "SHAPEZ2-4-H4sIAIVqo2kA/4yXQUvDQBCF/8vgcQUnGy97FHsoKBSVokiRRSMG4qZkk0MI+e8m9OShnY9CQ8jbmTfvDcPsJHsJqv7Gyd1OwiRX/XisJMg2NzF9iZPtZ5vWD/exjxLepV7ew66J/Xfb/WZxaWia05/kn3iswtNw+slhdrJJfVdXeTk4yauE61snb8ujdPKyJHmIYzv0H8/rucc6VZ3M7h/OQ1wBcQpwJJAyGKQFq4SimSWU0IMSelBCD0roASSmDAZpwSohN9MDDz3w0AMPPfDQA5hQGQzSgkmhaKYHBfSggB4U0IMCegADKYPBaLBKKJrpgUIPFHqg0AOFHigLBGGQFqwSinbRA1N8U3VTblPni0fVCG2ltrhbxVsdDBsY9i9sX9i9isIwFKPE6mNiWcrD8Q2nNxzecHazMIpQLBarj4llKQ+XF7i7wNUFbi4smyIUo8QyMrEs5eHqDjd3uLjDvZ2RUoRilFh9jNd55Q/L1bhOsRv3VZfr9TK83pfn+U8AAQYAk7SZ7zsPAAA=$"
const brush_fluid_blueprint = "SHAPEZ2-4-H4sIAAVro2kA/4yXT0vDQBDFv8vgcQUnay57FC0UFIpIUaTIYiMuxG3Jn0MI+e4m5OTBzo9AQsjLzJv3hmF2lL0EVX/j5G4nYZSrbjhXEmTb1jEfxcn285SXD/exixLeJc3vYVfH7uvU/LTicl/X603a73iuwnO/XnKYnDzkrklVO/84yquE61snb+vjZU7yGIdT331s6j4dn1KuGpncH5yHuALiFOBIIGUwSAtWCbmVFsxDDzz0wEMPPPQAJlQGg7RgUiia6UEBPSigBwX0oIAewEDKYDAarBKKZnqg0AOFHij0QKEHygJBGKQFq4SiXfTAFN9U3ZTb1Pnir2qEtlJb3K3irQ6GDQz7F7Yv7F5FYRiKUWL1MbEs5eH4htMbDm84u1kYRSgWi9XHxLKUh8sL3F3g6gI3F5ZNEYpRYhmZWJbycHWHmztc3OHezkgpQjFKrD7Gy1K+ZMqXTPmSKV8y5Rl3RShGidXHxPqf/WE+EKccm2FfNW1ajsDLKXmafgUQYACpKx0vMQ8AAA==$"

const miner_blueprints = {
    "Shape Miner": {
        "default_shape_miner": {
            name: "Post 1.0 cheapest version - by 404 - 76 Buildings",
            blueprint: "SHAPEZ2-4-H4sIAEkcIGoA/6yYb6vaMBTGv0vYy74wrf37stw7ECqIemVjXEaw8S6sS0uabhPxu6/aqrV/NDkdgqLml+eck5MnoQe0QQHGlmugcIGCA/ok9xlFAZrlCeExMtBsm/LTHy9EEhR8Q6z8HiwSInep+JUjgxdJUr2h/AfJaLAsqhd6PxrolUvBaF6CB7Qup43IPi3k99Vp5JxxKkqFsKkbFiyJGf/4r8pfyhynBvpafSxRYBnnaF7/SkG2MhUvdEeKRM64pIKTZEMEI1yio1Gx1gjWHMFiOOvDUQ+OunDUGZurfSYxIFUI6YJJB0zWPQxCLThqwlEMRydn1KmgkCZykQq5ojymYgix+5Al3VL2exiqdLClL9Rmnik57fDqCkR0167CnAmRChq3WLdZyMYMn1Pxh4h4SLjqVU8nw0rPH9Dribgl5uuLeU2xVZYwWY7G69R6vAoVZmrFaHezi9hOmm/ZI+pak6hPT2kNOrBqcZq9ppBgDZlNM9WNFWOdMGtmAmCwdlGuO0m3O93mFpxT8UGFuU5x9PB4UB7u6w2/rWzvIinYgnvXG8OKbc4Dcj6Qu1xkRqR6uUfpa1tQcNoT9PNVbeyE6K47lbf6ZESVnOuWuk2h7qU1Z4Kk7Z7oh111KPLJGHvt0s+LPn1slRqZm7ec8Vv2JOCbQ0e6J6zTarCxcePGRPc5hGT7UyEJDFszpyuv0bFui1ZfcQw9PWoPUjb42nrUx0+7kWn7lQvIy76Quv3rqrdvJ9zrrRRmk36jbYA3VJiw1xXWuq2O2mveGHv0NNzx3UAh40TsN1Tk7PQg5vSU6Dj4+z8BBgC7VdUdSRIAAA==$"
        },
        "pre1.0" : {
            name: "Pre 1.0 cheapest version - by 404 - 76 Buildings",
            blueprint: "SHAPEZ2-4-H4sIAF7HumkA/6yYX4viMBTFv0vYxz6YtvbfY5lZECqIujLDMixB42zYbipp3F0Rv/u2tjNTW6PJzSAoan6999yck0KPaIUSjD3fQekMJUf0RR52FCVoUuaEb5CDJuuC1388EElQ8h2x6nsyy4ncFuJ3iRy+z/PmDZU/yY4m833zQi8nBz1yKRgtK/CIltVlM3Io9vLHol45ZZyKqkLarZvuWb5h/PVTKz/VGh30XH1UQuco8ZxzN4//pCBrWYgHuiX7XE64pIKTfEUEI1yik9OwrgXrWbA+nA3gaAhHIzga22odn0kMkAohIzAZg8nWwyDUhaMeHPVttdbFP/yQ0ly2WEa3fXTKhCgE3fRj28JTKl6pcJcFzu6BHhT0rzStxntZtZAaAhuOoEKb3Qm6G3u7496mBLqzafdCf70/7ExfVwCVFZp1GZktjw1nMOqurwXMCiEXlG+oUCHja8icrin7o4RiqHtGF6BJg33mToc4GFAaFm0hV5HHr4X4S8RGRbdZxCbi2ooji8MufL+EftmPVrMLv+s2HIA6bdhQETKt6UbmvcaAsyp8I01HGkEnGnW7XOxyJqvVeFl4t2PRYK6RuPFwLBnbSvfb7n424rM+F7Z5A1g7H7ibD/3ptJwLcuv4SjTVc1KYvcbhAxvS9yfm24TMH3qxloxvW2N83fp6Jd8PhQa+nHVVOCXrX/f56G1QwKhHUGteqNZxZjdH2OZoMj1nfKubm38liGprqMKEbTzSpgF/yr0SdkpfCtDf7nrq/f028ndb2LXXjg2c/uKglHEiDisqSlY/lKmfGJ2Uv/8XQIABAJX1h1xVEgAA$"
        },
        "both" : {
            name: "Golden Unicorn - by IMarvinTPA - 167 Buildings ",
            blueprint: "SHAPEZ2-4-H4sIAFYbIGoA/6yaX2/bOAzAv4uwRz9YsiXbeczaDTmkQJH2chuG4eA26mbMswPFua4o+t0XJ3YmO/5D0ocCLdrmJ1IkRVK0X9mazTj3AofNb9nslb0rXraazdhil8bZhjls8Zhn5T+u4iJmsy8sOfw+u03j4ik3P3fMyfZpevrGdt/jrZ6t9qcv9vXNYddZYRK9O4Cv7P6w7DJ+yffFv3flJ2+STJuDhLktd75P0k2SfftfJX8q9+iwz4cfvsNWbOY5R22ufxUmfixyc6Wf4n1aLLJCmyxO17FJ4qxgb86JFRNYbwLr01lFRwM6GtLRaOpe5ZHkhK1SyJBMRmSyimESKuioR0d9OlpFYUXNdVrc5qa409lGm3FmyWaCTBJkhiSEpmVIVZK7NIYujbbBiCoyosrCKHk6+eoY0xV3o803bcR9zpct6CYxJjd600w4RFhNgatjTKXFJJpPoSMLtoKiyh9L/VSAFigN8Ke0DK/QqmceTPFWAUVSikT5dRSvGlFcbe1Dbp5js+lhpcVWhr3bpklx+DC/z8WYX+SlU2v8/tjgDYqVPd4YVrlMKmT45Be/nV1ArF+zfza7TJ4K/vd2IHxkna9XeIEnNoA6pxlFAUlYaVyCpnVrLWy6Ms48fvwBQF3bnyUqwOi52EOzQ7urR9UZ1cms9KNO/uunBLm7UAMkSqogSxUoqQpv1IhkU7cjXYLST036k4JdNsIclLS47DrMg7pGNigQImXDpqcyAkjKBHPKKdZUeGNKqi3r8+AS0pSwEjkuS4lml4lOUh6+sfWoTbRH7IitVNwqU96oWaCA6rLDWI5Q/ZbAoIKSmRQ1MQW0vOReNnNYmFr/3Y5k4x161sGkFuEDLKL4IaS2t5GFC1Knie3Cwh4KcMUJL/c6fneQdt/m4S2kzjwpXsByW9VQTHAJWtmwQ1dAOQ3PR4JwTwk7mmIkHIE1rYfMhNtxPdtGXlnrQozFOA3zp44PuLSdiWsc7Cs2rnGQrSEaunNQFzM/2OlUPXM/Ao3ODLKhM6Qv8K2aKVCuadyUUU4JLJ8IlE+GL/XeMBaSgyCk+eE8aKaLpYSQbI7HJwknRmDQozkiW7iW8TzSQqLZvZLX4a0ZAnkh15qBeehbrI++xIbNeV27tQEUYDkYwaBQUHYoHNW+yp8zcEsWDFodsv+GAoCdB+cLMuHwhS2Y0vT43VsGPliJ+umRhj+8SFpYg0eXBofdT/x+cOyW4vemC0yw1a0Yzeu1EhKe9ppz8c4JFUBt2YoYuMXdAXLM5LyHhdlKDNPwzN40N7iTJZ+vmufkE+Z3bB08W8TXDVVz8Ekr70DgNVJiG56eEmmvgxmkyTEa5B/ZVzDHnyOqbgOMKt6RxDglsvg0+R5Zvrx8mFRn4fhBpz3vqjjsfflGy/P84+afX7vF9V/fHz5+2H8W6x+La759+Ll+YW9fHTZPsti8rLXZJeUbbeXrdm+9f/8tgAADAL5jQDOSJwAA$"
        }
    },
    "Fluid Miner": {
        "default_fluid_miner": {
            name: "Default Fluid Miner",
            blueprint: "SHAPEZ2-4-H4sIAFVro2kA/6yXX2vCMBTFv8tlj30wrdraR/cHHA7EbbIxxgg2bmE1LWnKEPG7r7Xq4py19zoEpZqf5yTn3oQsYQIhY17Lgf4IwiVcmEUqIIRBFnMVgQODaaLKH6644RC+gCyew1HMzSzR8wwclcdx9QbZB09FOM6rF7yuHLhWRkuRFeASHoq/HfJFkpu3mziX0Z1UQhcKfVu3n8s4kur9X5Wfyjk68Axhx4Fx8eCszYzyeXolZjyPzUAZoRWPJ1xLrgysnIpySZRHotpnUOVHgXlIi2jMpWHsLIyRQkNjHg1rn4MFpNgCUmoBafWxVGdN+ZvxMhU3if7iOqofX1psCHS3ApatghqKmalHbI3To4Ofwbe5mhqZqGOAbwPrrW2UaHMvVCR0vUgPK9IjiLAWVmVLNJTxdx2A91a1jZXMpU6y7ESxHECPaZ9PP+uq5sfjcNelaKcVul93jYsDrbtLnOq4ZaO49NGSnf1p0uKpcJeejru3CZ/oc/8Xia/4Fhnt0We6J9ok1e6hYnMs+HtdMZqMpsmwmtV51cWUgGshiJ72aBizTi4XY9DHLoVHw9rWvFwsdnAi1+7kbHckY9PaMOi48NzGo4cPbMOgE8Nz7SMeG3IH6/93aK/FLU0qrhcToTNZXsvKO+Pq6PffAgwAKnl1QlcOAAA=$"
        }
    }
};

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
const dropdown_miner_blueprint = document.getElementById('miner_blueprint_dropdown');
const text_miner_blueprint = document.getElementById('miner_blueprint');
const button_generate_blueprint = document.getElementById('generate_blueprint');
const button_copy_blueprint = document.getElementById('copy_blueprint');
const text_blueprint = document.getElementById('blueprint_text');

const checkbox_solve_for_fluid = document.getElementById('solve_for_fluid');
checkbox_solve_for_fluid.addEventListener('click', () => {
    solve_for_fluid = checkbox_solve_for_fluid.checked;
    update_copy_brush_blueprint_text();
    update_default_dropdown_selection();
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
// populate the dropdown with miner blueprints
function populate_dropdown()
{
    for (const groupName in miner_blueprints) {
        const optgroup = document.createElement("optgroup");
        optgroup.label = groupName;
        for (const key in miner_blueprints[groupName]) {
            const option = document.createElement("option");
            option.value = key;
            option.textContent = miner_blueprints[groupName][key].name;
            optgroup.appendChild(option);
        }
        dropdown_miner_blueprint.appendChild(optgroup);
    }
}

// set initial dropdown state based on solve_for_fluid
function update_default_dropdown_selection() 
{
    if (solve_for_fluid) {
        dropdown_miner_blueprint.value = "default_fluid_miner";
    } else {
        dropdown_miner_blueprint.value = "default_shape_miner";
    }
    callback_dropdown_change();
}

populate_dropdown();
update_default_dropdown_selection();

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
dropdown_miner_blueprint.addEventListener('change', callback_dropdown_change);
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

function update_copy_brush_blueprint_text()
{
    if (solve_for_fluid)
    {
        button_copy_brush_blueprint.textContent = "Copy Fluid Brush Blueprint (Size = 10)";
    }
    else
    {
        button_copy_brush_blueprint.textContent = "Copy Brush Blueprint (Size = 10)";
    }
}

function callback_dropdown_change() 
{
    function get_blueprint_by_key(keyToFind) {
        for (const groupName in miner_blueprints) {
            if (miner_blueprints[groupName][keyToFind]) {
                return miner_blueprints[groupName][keyToFind].blueprint;
            }
        }
        return "";
    }

    const selectedKey = dropdown_miner_blueprint.value;
    text_miner_blueprint.value = get_blueprint_by_key(selectedKey);

    // Check if the selected key belongs to "Fluid Miner" group
    const isFluid = !!(miner_blueprints["Fluid Miner"] && miner_blueprints["Fluid Miner"][selectedKey]);
    
    // Update solve_for_fluid variable and checkbox state accordingly
    solve_for_fluid = isFluid;
    checkbox_solve_for_fluid.checked = solve_for_fluid;
    update_copy_brush_blueprint_text();
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

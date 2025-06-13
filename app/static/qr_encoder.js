// -----------------------------------------------
// data
// -----------------------------------------------
const stats_refresh_interval_in_seconds = 5; // seconds

// -----------------------------------------------
// get web page elements
// -----------------------------------------------
const input_text = document.getElementById('input_text');
const version = document.getElementById('version');
const error_correction_level = document.getElementById('error_correction_level');
const use_smallest_qr_code_possible = document.getElementById('use_smallest_qr_code_possible');
const qr_canvas = document.getElementById('qr_canvas');
const blueprint_type = document.getElementById('blueprint_type');
const generate_blueprint = document.getElementById('generate_blueprint');
const copy_blueprint = document.getElementById('copy_blueprint');
const blueprint_text = document.getElementById('blueprint_text');
const stats_qrs_generated_in_total = document.getElementById('stats_qrs_generated_in_total');
const stats_qrs_generated_today = document.getElementById('stats_qrs_generated_today');

// pull once at start
function pull_stats_once()
{
    fetch('/get_qr_stats/')
    .then(response => response.json())
    .then(data => {
        stats_qrs_generated_in_total.textContent = data.qr_codes_ran_in_total;
        stats_qrs_generated_today.textContent = data.qr_codes_ran_today;
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
// callback functions
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

function get_input_text_value()
{
    // if input_text_value is empty, use placeholder
    const input_text_value = input_text.value;
    if (input_text_value == "") 
    {
        return input_text.placeholder;
    }
    return input_text_value;
}

async function callback_generate_qr() 
{
    form = new FormData();
    form.append('input_text', get_input_text_value());
    form.append('version', version.value); 
    form.append('error_correction_level', error_correction_level.value); 
    
    const response = await fetch(`/generate_qr_code_image/`, {method: 'POST', body: form});

    if (!response.ok) 
    {
        console.error('Failed to generate QR code image');
        return;
    }

    const data = await response.json();
    const qr_code_image_base64 = data.qr_code_image;
    const version_used = data.version_used;
    update_canvas_image(qr_canvas, qr_code_image_base64);
    version.value = version_used;
}

input_text.addEventListener('change', async function() 
{
    callback_generate_qr();
})

version.addEventListener('change', async function() 
{
    callback_generate_qr();
})

error_correction_level.addEventListener('change', async function() 
{
    callback_generate_qr();
})

use_smallest_qr_code_possible.addEventListener('click', async function() 
{
    version.value = '1';
    error_correction_level.value = 'L';
    callback_generate_qr();
})

generate_blueprint.addEventListener('click', async function() 
{
    callback_generate_blueprint();
})

copy_blueprint.addEventListener('click', async function() 
{
    callback_copy_blueprint();
})

async function callback_generate_blueprint()
{
    form = new FormData();
    form.append('input_text', get_input_text_value()); 
    form.append('version', version.value); 
    form.append('error_correction_level', error_correction_level.value); 
    form.append('blueprint_type', blueprint_type.value); 
    
    const response = await fetch(`/generate_qr_code_blueprint/`, {method: 'POST', body: form});

    if (!response.ok) 
    {
        console.error('Failed to generate QR code blueprint');
        return;
    }

    const data = await response.json();
    blueprint_text.textContent = data.blueprint;    
}



function callback_copy_blueprint() 
{
    // ----------------------------------------------------
    // local processing
    // ----------------------------------------------------

    // won't work if no blueprint
    if (!blueprint_text.textContent) 
    {
        console.error('No blueprint available to copy.');
        return;
    }

    // copy the blueprint to clipboard
    navigator.clipboard.writeText(blueprint_text.textContent)
        .then(() => {
            console.log('Blueprint copied to clipboard successfully!');
        })
        .catch(err => {
            console.error('Failed to copy blueprint:', err);
        });
}
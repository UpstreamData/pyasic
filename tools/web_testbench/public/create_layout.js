import { generate_graphs } from "./generate_graphs.js"


function pauseMiner(ip, checkbox) {
    // if the checkbox is checked we need to pause, unchecked is unpause
    if (checkbox.checked){
        sio.emit("pause", ip)
    } else if (!(checkbox.check)) {
        sio.emit("unpause", ip)
    }
}

function checkPause(ip, checkbox) {
    // make sure the checkbox exists, removes an error
    if (checkbox) {
        // get status of pause and set checkbox to this status
        sio.emit("check_pause", ip, (result) => {
                checkbox.checked = result
            }
        );
    }
}

function lightMiner(ip, checkbox) {
    // if the checkbox is checked turn the light on, otherwise off
    if (checkbox.checked){
        sio.emit("light", ip)
    } else if (!(checkbox.check)) {
        sio.emit("unlight", ip)
    }
}

function checkLight(ip, checkbox) {
    // make sure the checkbox exists, removes an error
    if (checkbox) {
        // get status of light and set checkbox to this status
        sio.emit("check_light", ip, (result) => {
                checkbox.checked = result
            }
        );
    }
}

export function generate_layout(miners) {
    // get the container for all the charts and data
    var container_all = document.getElementById('chart_container');
    // empty the container out
    container_all.innerHTML = ""

    miners.forEach(function(miner) {

        // create main div column for all data to sit inside
        var column = document.createElement('div');
        column.className = "col border border-dark p-3"

        // create IP address header
        var header = document.createElement('button');
        header.className = "text-center btn btn-primary w-100"
        header.onclick = function(){window.open("http://" + miner.IP, '_blank');}
        header.innerHTML += miner.IP

        // add the header to col first
        column.append(header)

        // create light button container
        var container_light = document.createElement('div');
        container_light.className = "form-check form-switch d-flex justify-content-evenly"

        // create light button
        var light_switch = document.createElement('input');
        light_switch.type = "checkbox"
        light_switch.id = "light_" + miner.IP
        light_switch.className = "form-check-input"

        // check if the light is turned on and add click listener
        checkLight(miner.IP, light_switch);
        light_switch.addEventListener("click", function(){lightMiner(miner.IP, light_switch);}, false);

        // add a light label to the button
        var label_light = document.createElement("label");
        label_light.setAttribute("for", "light_" + miner.IP);
        label_light.innerHTML = "Light";

        // add the button and label to the container
        container_light.append(light_switch)
        container_light.append(label_light)

        if (miner.hasOwnProperty('text')) {
            // create text row
            var row_text = document.createElement('div');
            row_text.className = "row"

            // create text container
            var text_container = document.createElement('div')
            text_container.className = "col w-100 p-3"


            // create text area for data
            var text_area = document.createElement('textarea');
            text_area.rows = "10"
            text_area.className = "form-control"
            text_area.style = "font-size: 12px"
            text_area.disabled = true
            text_area.readonly = true

            // add data to the text area
            var text = miner.text
            text += text_area.innerHTML
            text_area.innerHTML = text

            // add the text area to the row
            row_text.append(text_area)

            // create a row for buttons
            var row_buttons = document.createElement('div');
            row_buttons.className = "row mt-3"

            // create pause button container
            var container_pause = document.createElement('div');
            container_pause.className = "form-check form-switch d-flex justify-content-evenly"

            // create the pause button
            var pause_switch = document.createElement('input');
            pause_switch.type = "checkbox"
            pause_switch.id = "pause_" + miner.IP
            pause_switch.className = "form-check-input"

            // check if it is paused and add the click listener
            checkPause(miner.IP, pause_switch);
            pause_switch.addEventListener("click", function(){pauseMiner(miner.IP, pause_switch);}, false);

            // add a pause label
            var label_pause = document.createElement("label");
            label_pause.setAttribute("for", "pause_" + miner.IP);
            label_pause.innerHTML = "Pause";

            // add the label and button to the container
            container_pause.append(pause_switch);
            container_pause.append(label_pause);
            text_container.append(row_text);

            // add the container to the row
            row_buttons.append(container_pause);

            if (miner.Light == "show") {
                // add the light container to the row
                row_buttons.append(container_light)
            }

            //add the row to the main column
            column.append(text_container);
            column.append(row_buttons);

            // add the column onto the page
            container_all.append(column);

        } else {
            // get fan rpm
            var fan_rpm_1 = miner.Fans.fan_0.RPM;
            var fan_rpm_2 = miner.Fans.fan_1.RPM;

            // create hr canvas
            var hr_canvas = document.createElement('canvas');

            // create temp canvas
            var temp_canvas = document.createElement('canvas');

            // create fan 1 title
            var fan_1_title = document.createElement('p');
            fan_1_title.innerHTML += "Fan L: " + fan_rpm_1 + " RPM";
            fan_1_title.className = "text-center"

            // create fan 2 title
            var fan_2_title = document.createElement('p');
            fan_2_title.innerHTML += "Fan R: " + fan_rpm_2 + " RPM";
            fan_2_title.className = "text-center"

            // create fan 1 canvas
            var fan_1_canvas = document.createElement('canvas');

            // create fan 2 canvas
            var fan_2_canvas = document.createElement('canvas');


            // create row for hr and temp data
            var row_hr = document.createElement('div');
            row_hr.className = "row"

            // create row for titles of fans
            var row_fan_title = document.createElement('div');
            row_fan_title.className = "row"

            // create row for fan graphs
            var row_fan = document.createElement('div');
            row_fan.className = "row"

            // create hr container
            var container_col_hr = document.createElement('div');
            container_col_hr.className = "col w-50 ps-0 pe-4"

            // create temp container
            var container_col_temp = document.createElement('div');
            container_col_temp.className = "col w-50 ps-0 pe-4"

            // create fan title 1 container
            var container_col_title_fan_1 = document.createElement('div');
            container_col_title_fan_1.className = "col"

            // create fan title 2 container
            var container_col_title_fan_2 = document.createElement('div');
            container_col_title_fan_2.className = "col"

            // create fan 1 data container
            var container_col_fan_1 = document.createElement('div');
            container_col_fan_1.className = "col w-50 ps-3 pe-1"

            // create fan 2 data container
            var container_col_fan_2 = document.createElement('div');
            container_col_fan_2.className = "col w-50 ps-3 pe-1"

            // append canvases to the appropriate container columns
            container_col_hr.append(hr_canvas)
            container_col_temp.append(temp_canvas)
            container_col_title_fan_1.append(fan_1_title)
            container_col_title_fan_2.append(fan_2_title)
            container_col_fan_1.append(fan_1_canvas)
            container_col_fan_2.append(fan_2_canvas)

            // add container columns to the correct rows
            row_hr.append(container_col_hr)
            row_hr.append(container_col_temp)
            row_fan_title.append(container_col_title_fan_1)
            row_fan_title.append(container_col_title_fan_2)
            row_fan.append(container_col_fan_1)
            row_fan.append(container_col_fan_2)

            // append the rows to the columns
            column.append(row_hr)
            column.append(row_fan_title)
            column.append(row_fan)

            // create a row for buttons
            var row_buttons = document.createElement('div');
            row_buttons.className = "row mt-3"

            if (miner.Light == "show") {
                // add the light container to the row
                row_buttons.append(container_light)
            }
            // add the row to the main column
            column.append(row_buttons)

            // add the column to the page
            container_all.append(column);

            // generate the graphs
            generate_graphs(miner, hr_canvas, temp_canvas, fan_1_canvas, fan_2_canvas);
        }
    });
<<<<<<< HEAD
}

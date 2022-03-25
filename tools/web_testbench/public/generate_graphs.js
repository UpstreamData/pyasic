import { options_hr, options_temp, options_fans } from "./graph_options.js";

// generate graphs used for the layout
export function generate_graphs(miner, hr_canvas, temp_canvas, fan_1_canvas, fan_2_canvas) {

    var hr_data = []

    var count = 0
    // get data on all 3 boards
    for (const board_num of [6, 7, 8]) {
        // check if that board exists in the data
        if (("board_" + board_num) in miner.HR) {
            // set the key used to get the data
            var key = "board_"+board_num

            // add the hr info to the hr_data
            hr_data.push({label: board_num, data: [miner.HR[key].HR], backgroundColor: []})

            // set the colors to be used in the graphs (shades of blue)
            if (board_num == 6) {
                hr_data[count].backgroundColor = ["rgba(0, 19, 97, 1)"]
            } else if (board_num == 7) {
                hr_data[count].backgroundColor = ["rgba(0, 84, 219, 1)"]
            } else if (board_num == 8) {
                hr_data[count].backgroundColor = ["rgba(36, 180, 224, 1)"]
            }
            count += 1
        }
    }

    // create the hr chart
    var chart_hr = new Chart(hr_canvas, {
        type: "bar",
        data: {
            labels: ["Hashrate"],
            // data from above
            datasets: hr_data
        },
        // options imported from graph_options.js
        options: options_hr
    });


    var temps_data = []

    // get temp data for each board
    for (const board_num of [6, 7, 8]) {

        // check if the board is in the keys list
        if (("board_" + board_num) in miner.Temps) {

            // set the key to be used to access the data
            key = "board_"+board_num

            // add chip and board temps to the temps_data along with colors
            temps_data.push({label: board_num + " Chip", data: [miner.Temps[key].Chip], backgroundColor: ["rgba(6, 92, 39, 1)"]});
            temps_data.push({label: board_num + " Board", data: [miner.Temps[key].Board], backgroundColor: ["rgba(255, 15, 58, 1)"]});
        }
    }


    var chart_temp = new Chart(temp_canvas, {
        type: "bar",
        data: {
            labels: ["Temps"],
            // data from above
            datasets: temps_data
        },
        // options imported from graph_options.js
        options: options_temp,
    });

    // get fan rpm
    var fan_rpm_1 = miner.Fans.fan_0.RPM;
    if (fan_rpm_1 == 0){
        var secondary_col_1 = "rgba(97, 4, 4, 1)"
    } else {
        var secondary_col_1 = "rgba(199, 199, 199, 1)"
    }
    var fan_rpm_2 = miner.Fans.fan_1.RPM;
    if (fan_rpm_2 == 0){
        var secondary_col_2 = "rgba(97, 4, 4, 1)"
    } else {
        var secondary_col_2 = "rgba(199, 199, 199, 1)"
    }

    // set the fan data to be rpm and the rest to go up to 6000
    var fan_data_1 = [fan_rpm_1, (6000-fan_rpm_1)];

    // create the fan 1 chart
    var chart_fan_1 = new Chart(fan_1_canvas, {
        type: "doughnut",
        data: {
            labels: ["Fan L"],
            datasets: [
                {
                    // data from above, no colors included
                    data: fan_data_1,
                    // add colors
                    backgroundColor: [
                        "rgba(103, 0, 221, 1)",
                        secondary_col_1
                    ]
                },
            ]
        },
        // options imported from graph_options.js
        options: options_fans
    });


    var fan_data_2 = [fan_rpm_2, (6000-fan_rpm_2)];

    // create the fan 2 chart
    var chart_fan_2 = new Chart(fan_2_canvas, {
        type: "doughnut",
        data: {
            labels: ["Fan R"],
            datasets: [
                {
                    // data from above, no colors included
                    data: fan_data_2,
                    // add colors
                    backgroundColor: [
                        "rgba(103, 0, 221, 1)",
                        secondary_col_2
                    ]
                },
            ]
        },
        // options imported from graph_options.js
        options: options_fans
    });
}


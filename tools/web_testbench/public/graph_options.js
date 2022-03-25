// All options for creation of graphs in ./generate_graphs.js

export var options_hr = {
    animation: {
        duration: 0,
    },
    responsive: true,
    aspectRatio: .75,
    plugins: {
        legend: {
            display: false,
        }
    },
    scales: {
        y: {
            ticks: { stepSize: .6 },
            min: 0,
            suggestedMax: 3.6,
            grid: {
                color: function(context) {
                    if (context.tick.value == 2.4) {
                        return "rgba(0, 0, 0, 1)";
                    } else if (context.tick.value > 2.4) {
                        return "rgba(103, 221, 0, 1)";
                    } else if (context.tick.value < 2.4) {
                        return "rgba(221, 0, 103, 1)";
                    }
                }
            }
        }
    }
};

export var options_temp = {
    animation: {
        duration: 0,
    },
    responsive: true,
    plugins: {
        legend: {
            display: false,
        }
    },
    aspectRatio: .75,
};

export var options_fans = {
    animation: {
        duration: 0,
    },
    aspectRatio: 1.5,
    events: [],
    responsive: true,
    plugins: {
        legend: {
            display: false,
        }
    }
};
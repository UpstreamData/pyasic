import {generate_layout} from "./create_layout.js"

// when miner data is sent
ws.onmessage = function(event) {
    // generate the layout of the page
    generate_layout(JSON.parse(event.data));
});

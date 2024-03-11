///
/// Called when the user wants to send the collected components to the orchestration script.
///
function trigger_orchestration() {
    main_config = {};
    var sub_config = {};

    // Extract the database location of the selected first server
    var server_1 = document.getElementById("server_1");
    sub_config["server_1"] = server_1.value;

    // Extract the database location of the selected first router
    var router_1 = document.getElementById("router_1")
    sub_config["router_1"] = router_1.value;

    // Extract the database location of the selected first switch
    var switch_1 = document.getElementById("switch_1")
    sub_config["switch_1"] = switch_1.value;

    // Extract the database location of the selected first charge controller
    var charge_controller_1 = document.getElementById("charge_controller_1")
    sub_config["charge_controller_1"] = charge_controller_1.value;

    main_config["config"] = sub_config;

    // let the user know something is happening
    document.getElementById("spinner").classList.add("loader");

    // Send the request for the auto-generated documentation, and include the configuration data in it
    const xhr = new XMLHttpRequest();
    xhr.open("POST", "/wakoma/nimble");
    xhr.setRequestHeader("Content-Type", "application/json;charset=UTF-8");
    xhr.send(JSON.stringify(main_config));
    xhr.responseType = "json";
    xhr.onload = () => {
        if (xhr.readyState == 4 && xhr.status == 200) {
            poll(xhr.response);
        } else {
            // The loading indicator is no longer needed
            document.getElementById("spinner").classList.remove("loader");

            console.log(`Error: ${xhr.status}`);
        }
    };
}

function poll(response_object) {
    var poll_url_end = response_object[0]["redirect"];
    var config_hash = poll_url_end.split("=")[1]

    // Try to load the file location
    const xhr = new XMLHttpRequest();
    xhr.open("GET", poll_url_end, true);
    xhr.responseType = 'blob';
    xhr.send();
    xhr.onload = () => {
        // If the file is ready, download it now
        if (xhr.readyState == 4 && xhr.status == 200) {
            // The loading indicator is no longer needed
            document.getElementById("spinner").classList.remove("loader");

            // Boiler plate to force a download
            const url = window.URL.createObjectURL(xhr.response);
            const a = document.createElement('a');
            a.style.display = 'none';
            a.href = url;
            a.download = config_hash + '.zip';
            document.body.appendChild(a);
            a.click();
            window.URL.revokeObjectURL(url);
        }
        // Wait and try again later if the file is not ready
        else if (xhr.status == 307) {
            setTimeout(poll, 5000, response_object);
        }
        else {
            // The loading indicator is no longer needed
            document.getElementById("spinner").classList.remove("loader");

            console.log(`Error: ${xhr.statusText}`);
        }
    };

    console.log(response_object[0]["redirect"]);
}
///
/// Called when the user wants to send the collected components to the orchestration script.
///
function trigger_orchestration() {
    main_config = {};
    var sub_config = [];

    // Extract the database location of the selected first access point
    var ap_1 = document.getElementById("ap_1");
    if (ap_1.value !== "none") {
        sub_config.push(ap_1.value);
    }

    // Extract the database location of the selected first router
    var router_1 = document.getElementById("router_1");
    if (router_1.value !== "none") {
        sub_config.push(router_1.value);
    }

    // Extract the database location of the selected first server
    var server_1 = document.getElementById("server_1");
    if (server_1.value !== "none") {
        sub_config.push(server_1.value);
    }

    // Extract the database location of the selected first switch
    var switch_1 = document.getElementById("switch_1")
    if (switch_1.value !== "none") {
        sub_config.push(switch_1.value);
    }

    // Extract the database location of the selected first charge controller
    // var charge_controller_1 = document.getElementById("charge_controller_1")
    // sub_config["charge_controller_1"] = charge_controller_1.value;

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

//
// Allows the page to poll to see when the zip file is
// ready for download
//
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

            // Update the 3D viewer
            document.getElementById("model-viewer").src = "/wakoma/nimble/preview?config=" + config_hash;

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
}

//
// Takes a component key with spaces and other non-allowed characters
// and fixes it
//
function clean_up_key(component_key) {
    var new_key = component_key.replaceAll(" ", "_");
    return new_key;
}

//
// Allows the page to pull the component JSON data and
// populate the UI
//
function load_ui() {
    // URL to retrieve the omponent JSON data
    const comp_url = "/wakoma/nimble/components"

    // Set up the request for the component JSON data
    const xhr = new XMLHttpRequest();
    xhr.open("GET", comp_url, true);
    xhr.responseType = 'json';
    xhr.send();
    xhr.onload = () => {
        // If the file is ready, download it now
        if (xhr.readyState == 4 && xhr.status == 200) {
            xhr.response[0].forEach(element => {
                // Add entries to the appropriate drop-downs based on type

                // Check to make sure all the necessary attributes are available
                if (element["HeightUnits"] === "") {
                    return;
                }
                // Access point or router + access point combo
                if (element["Type"] == "Access Point" || element["Type"] == "Router + AP") {
                    var opt = document.createElement('option');
                    opt.value = clean_up_key(element["ID"]);
                    opt.innerHTML = element["Brand"].concat(" ", element["Hardware"]);

                    document.getElementById("ap_1").appendChild(opt);
                }
                // Router or router + access point combo
                else if (element["Type"] == "Router" || element["Type"] == "Router + AP") {
                    var opt = document.createElement('option');
                    opt.value = clean_up_key(element["ID"]);
                    opt.innerHTML = element["Brand"].concat(" ", element["Hardware"]);

                    document.getElementById("router_1").appendChild(opt);
                }
                // Server
                else if (element["Type"] == "Server") {
                    var opt = document.createElement('option');
                    opt.value = clean_up_key(element["ID"]);
                    opt.innerHTML = element["Brand"].concat(" ", element["Hardware"]);

                    document.getElementById("server_1").appendChild(opt);
                }
                // Switch
                else if (element["Type"] == "Switch") {
                    var opt = document.createElement('option');
                    opt.value = clean_up_key(element["ID"]);
                    opt.innerHTML = element["Brand"].concat(" ", element["Hardware"]);

                    document.getElementById("switch_1").appendChild(opt);
                }
            });
        }
        else {
            console.log(`Error: ${xhr.statusText}`);
        }
    };
}

// Triggers a load of the component JSON data into the UI
window.onload = function() {
    load_ui();
  };
var devices_json = null;


/*
 * Called when the user wants to send the collected components to the orchestration script.
 */
function trigger_orchestration() {
    main_config = {};
    var sub_config = [];

    // Walk through the drop downs that have been added to the components div
    select_elements = document.getElementById("components").querySelectorAll('select')
    select_elements.forEach(element => {
        // If the select is not set to None, save it into the config
        if (element.value !== "none") {
            sub_config.push(element.value);
        }
    });
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


/*
 * Allows the page to poll to see when the zip file is
 * ready for download
 */
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

            // Show the Download button
            document.getElementById("view-docs").style.visibility = "visible";
            document.getElementById("view-docs").onclick = function() { var link = document.createElement("a")
                                                                       link.href = "/static/builds/" + config_hash + "_assembly_docs/index.html"
                                                                       link.target = "_blank"
                                                                       link.click()};

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


/*
 * Takes a component key with spaces and other non-allowed characters
 * and fixes it
 */
function clean_up_key(component_key) {
    var new_key = component_key.replaceAll(" ", "_");
    return new_key;
}


/*
 * Allows the page to pull the component JSON data and save it for later use.
 */
function load_json() {
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
                // Save the JSON to use it for loading dynamic controls
                devices_json = xhr.response[0];
            });
        }
        else {
            console.log(`Error: ${xhr.statusText}`);
        }
    };
}


/*
 * Removes any drop downs that the user has set to None.
 */
function remove_unused_drops() {
    // Walk through the drop downs and remove any that have been set to None
    select_elements = document.getElementById("components").querySelectorAll('select')
    select_elements.forEach(element => {
        // If the select is not set to None, save it into the config
        if (element.value === "none") {
            element.remove();
            document.getElementById(element.id + "_lbl").remove();
        }
    });
}


/*
 * Loads a given select element up based on the devices.json data that was stored when
 * the page loaded.
 */
function load_select(drop_id, component_type, secondary_type) {
    devices_json.forEach(element => {
        // Check to make sure all the necessary attributes are available
        if (element["HeightUnits"] === "") {
            return;
        }

        if (element["Type"] == component_type || element["Type"] === secondary_type) {
            // Create a new option to be added to the select in question
            var opt = document.createElement('option');
            opt.value = clean_up_key(element["ID"]);
            opt.innerHTML = element["Brand"].concat(" ", element["Hardware"]);

            document.getElementById(drop_id).appendChild(opt);
        }
    });
}


/*
 * Allows a new component drop down to be created dynamically.
 */
function create_new_drop(drop_class, drop_label) {
    // Figure out how many AP drop downs there are so we can create an incremented name
    num_drops = document.getElementsByClassName(drop_class).length + 1;

    // Construct the drop down name
    drop_name = drop_class + num_drops;

    // Create the dynamic select element
    var lbl = document.createElement('label');
    lbl.for = drop_name;
    lbl.id = drop_name + "_lbl";
    lbl.innerHTML = drop_label;
    var drop = document.createElement('select');
    drop.id = drop_name;
    drop.classList.add(drop_class);
    drop.onchange = remove_unused_drops;
    var opt = document.createElement('option');
    opt.value = "none";
    opt.innerHTML = "None";

    // Add the select element to the list of controls
    document.getElementById("components").appendChild(lbl);
    document.getElementById("components").appendChild(drop);
    document.getElementById(drop_name).appendChild(opt);
}


/*
 * Allows the user to add access point drop-downs dynamically to the user interface.
 */
function add_access_point() {
    console.log("Adding access point...");

    // Create the new select element that will hold the access point components
    create_new_drop("ap_", "Access Point");

    // Load the select from the saved devices JSON
    load_select("ap_" + num_drops, "Access Point", "Router + AP");
}


/*
 * Allows the user to add router drop-downs dynamically to the user interface.
 */
function add_router() {
    console.log("Adding router...");

    // Create the new select element that will hold the router components
    create_new_drop("router_", "Router");

    // Load the select from the saved devices JSON
    load_select("router_" + num_drops, "Router", "Router + AP");
}


/*
 * Allows the user to add server drop-downs dynamically to the user interface.
 */
function add_server() {
    console.log("Adding server...");

    // Create the new select element that will hold the router components
    create_new_drop("server_", "Server");

    // Load the select from the saved devices JSON
    load_select("server_" + num_drops, "Server", "");
}


/*
 * Allows the user to add switch drop-downs dynamically to the user interface.
 */
function add_switch() {
    console.log("Adding switch...");

    // Create the new select element that will hold the router components
    create_new_drop("switch_", "Switch");

    // Load the select from the saved devices JSON
    load_select("switch_" + num_drops, "Switch", "");
}


/*
 * Triggers a load of the component JSON data into the UI.
 */
window.onload = function() {
    load_json();
}

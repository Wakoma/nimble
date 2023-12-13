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

    // Send the request for the auto-generated documentation, and include the configuration data in it
    const xhr = new XMLHttpRequest();
    xhr.open("POST", "/wakoma/nimble");
    xhr.setRequestHeader("Content-Type", "application/json;charset=UTF-8");
    xhr.send(JSON.stringify(main_config));
    xhr.responseType = "json";
    xhr.onload = () => {
        if (xhr.readyState == 4 && xhr.status == 200) {
            console.log(xhr.response);
        } else {
            console.log(`Error: ${xhr.status}`);
        }
    };
}
console.log("hello")

function trigger_gps_handler()
{
    document.getElementById('extract-gps-from-images-btn').innerHTML = "updated"
    $.ajax({
        type: "POST",
        url: "/im_meta_data_checker.py",
        data: { param: input },
        success: callbackFunc
    });
}

function callbackFunc(response) {
    document.getElementById('extract-gps-from-images-btn').innerHTML = "finished"
}
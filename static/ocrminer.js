
var TOKEN

window.onloadTurnstileCallback = function () {
    turnstile.render('#cf', {
        sitekey: '0x4AAAAAAAJSi6qwQ5B6stNP',
        callback: function (token) {
            //console.log(`Challenge Success ${token}`);
            TOKEN = token
        },
    });
};

function uploadImage() {

    $("#messagecontainer").fadeIn(300);

    const startTime = performance.now();
    const fileInput = document.getElementById('formFile');
    const file = fileInput.files[0];

    $("#notif").text('Waiting for server !');

    if (file) {
        $(':input[type="submit"]').prop('disabled', true);
        const formData = new FormData();
        turnstile.reset()
        formData.append('file', file);
        formData.append('cftoken', TOKEN);
        fetch('/api/v1/upload', {
            method: 'POST',
            body: formData
        })

            .then(response => response.json())
            .then(data => {
                // xss 
                $("#message-2").text(JSON.stringify(data, null, 4));
                $("#notif").text('Success !');
                const endTime = performance.now();
                const elapsedTime = endTime - startTime;

                tmp = "Success !\t Total elapsed time : " + elapsedTime / 1000 + "s";
                $("#notif").text(tmp);
                $(':input[type="submit"]').prop('disabled', false);
            })
            .catch(error => {

                $("#notif").text(error);
                $(':input[type="submit"]').prop('disabled', false);
            });
    } else {
        $("#notif").text('Please select a file ');
    }


    // $("#messagecontainer").fadeOut(10000);


}
function notification() {

}

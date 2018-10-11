

$(document).ready(function () {

    if (window.location.pathname === '/'){index()}

});

function index() {
    var fileInputElement = $("#inputFileOnboard");

    fileInputElement.change(function() {
        var file = fileInputElement[0].files[0];
        var filenameElement = $('#filenameOnboard');

        filenameElement.val(file.name);
    });

}
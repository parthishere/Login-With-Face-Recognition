console.log("okkk");

var loc = window.location;

var endPoint = '';
var wsStart = 'ws://';

if(loc.protocol == 'https:'){
    wsStart = 'wss://';
}

var endPoint = wsStart + loc.host + loc.pathname;
console.log(endPoint)

var socket = new WebSocket('ws://localhost:8888/websocket');


$(document).ready(function () {
    let video = document.getElementById('video');
    let canvas = document.getElementById('canvas');
    let context = canvas.getContext('2d');
    let draw_canvas = document.getElementById('detect-data');
    let draw_context = draw_canvas.getContext('2d');
    let image = new Image();
    if (navigator.mediaDevices && navigator.mediaDevices.getUserMedia) {
        navigator.mediaDevices.getUserMedia({video: true}).then(function (stream) {
            video.srcObject = stream;
            video.play();
        });
    }

    function drawCanvas() {
        context.drawImage(video, 0, 0, 600, 450);
        sendMessage(canvas.toDataURL('image/png'));
    }

    document.getElementById("start-stream").addEventListener("click", function () {
        drawCanvas();
    });

    function sendMessage(message) {
        socket.send(message);
    }
    socket.onmessage = function (e) {
        image.onload = function () {
            draw_context.drawImage(image, 0, 0, 600, 450);
        };
        image.src = e.data;
        //console.log(image.src)
        drawCanvas();
    };
})

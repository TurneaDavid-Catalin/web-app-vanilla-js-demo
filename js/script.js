function getCurrentTime() {
    let currentDate = new Date();
    let dateTime = currentDate.getDay() + '/' + currentDate.getMonth()
        + '/' + currentDate.getFullYear() + '@' + currentDate.getHours()
        + ':' + currentDate.getMinutes() + ':' + currentDate.getSeconds();

    document.getElementById("dateAndTime").innerHTML = dateTime;
}

function displayCurrentTime() {
    window.setInterval(getCurrentTime, 1000);
}

function getURL() {
    document.getElementById("currentURL").innerHTML = window.location.href;
}

function getCurrentLocation() {
    if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(success, error);
    } else {
        document.getElementById("currentLocation").innerHTML = "Geolocation is not supported by this browser.";
    }
}

function success(position) {
    document.getElementById("currentLocation").innerHTML = "Latitudine: " + position.coords.latitude +
        "<br>Longitudine: " + position.coords.longitude;
}

function error() {
    alert("Sorry, no position available.");
}

function getBrowserNameAndVersion() {
    let browserName = navigator.appName;
    let browserVersion = navigator.appVersion;

    document.getElementById("browserNV").innerHTML = browserName + ' ' + browserVersion;
}

function getOS() {
    document.getElementById("OS").innerHTML = navigator.platform;
}

function sectiunea1() {
    displayCurrentTime();
    getURL();
    getCurrentLocation();
    getBrowserNameAndVersion();
    getOS();
}

let clickCount = 0;
let startX = 0;
let startY = 0;

function getContourColour() {
    return document.getElementById("contColour").value;
}

function getFillColour() {
    return document.getElementById("fillColour").value;
}

function getMousePos(canvas, evt) {
    var rect = canvas.getBoundingClientRect();
    return {
        x: evt.clientX - rect.left,
        y: evt.clientY - rect.top
    };
}

function drawRect(evt) {
    const canvas = document.getElementById("myCanvas");
    const ctx = canvas.getContext("2d");
    const pos = getMousePos(canvas, evt);

    if (clickCount === 0) {
        startX = pos.x;
        startY = pos.y;
        clickCount = 1; 
    } 
    else {
        const endX = pos.x;
        const endY = pos.y;
        
        const width = endX - startX;
        const height = endY - startY;

        ctx.strokeStyle = getContourColour();
        ctx.fillStyle = getFillColour();
        ctx.lineWidth = 3; 

        ctx.beginPath();
        ctx.rect(startX, startY, width, height);
        ctx.fill();
        ctx.stroke();

        clickCount = 0;
    }
}
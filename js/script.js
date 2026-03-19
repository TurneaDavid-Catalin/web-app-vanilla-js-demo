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

function invata() {
    displayCurrentTime();
    getURL();
    getCurrentLocation();
    getBrowserNameAndVersion();
    getOS();
}
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

function insertRow() {
    // Preluam datele din input-uri
    let pos = parseInt(document.getElementById("insertPos").value);
    let color = document.getElementById("insertColor").value;
    let table = document.getElementById("boxingTable");
    
    // Folosim Node Lists pentru a prelua corpul tabelului si randurile
    let tbody = table.getElementsByTagName("tbody")[0];
    let rows = tbody.children; // NodeList cu randurile din tbody
    
    // Validam pozitia
    if (pos < 0) pos = 0;
    if (pos > rows.length) pos = rows.length;

    // Cream o linie noua (nod HTML)
    let newRow = document.createElement("tr");
    newRow.className = "delimiter-row"; // Clasa pentru inaltime mica

    // Aflam cate coloane are tabelul citind nodurile (children) primei linii
    let colCount = table.rows[0].children.length;

    // Cream exact atatea celule cate coloane exista
    for (let i = 0; i < colCount; i++) {
        let newCell = document.createElement("td");
        
        // ATENTIE: Modificam culoarea de fundal pentru fiecare celula in parte (cerinta JS HTML DOM - Changing CSS)
        newCell.style.backgroundColor = color; 
        
        // Adaugam celula la noul rand
        newRow.appendChild(newCell);
    }

    // Navigare DOM: Inseram randul la pozitia dorita
    if (pos === rows.length) {
        tbody.appendChild(newRow); // Punem la final
    } else {
        tbody.insertBefore(newRow, rows[pos]); // Inseram inaintea elementului de la indexul dat
    }
}

function insertCol() {
    let pos = parseInt(document.getElementById("insertPos").value);
    let color = document.getElementById("insertColor").value;
    let table = document.getElementById("boxingTable");
    
    let rows = table.getElementsByTagName("tr"); 

    for (let i = 0; i < rows.length; i++) {
        let currentRow = rows[i];
        let cells = currentRow.children; 
        
        let targetPos = pos;
        if (targetPos < 0) targetPos = 0;
        if (targetPos > cells.length) targetPos = cells.length;

        let isHeader = currentRow.parentNode.tagName.toLowerCase() === 'thead';
        let newCell = document.createElement(isHeader ? "th" : "td");
        
        newCell.className = "delimiter-col"; 
        newCell.style.backgroundColor = color; 

        if (targetPos === cells.length) {
            currentRow.appendChild(newCell);
        } else {
            currentRow.insertBefore(newCell, cells[targetPos]);
        }
    }
}

function verificaUtilizator() {
    const username = document.getElementById("username").value;
    const password = document.getElementById("password").value;
    const output = document.getElementById("checkID");

    const xhttp = new XMLHttpRequest();
    xhttp.onreadystatechange = function () {
        if (this.readyState === 4) {
            if (this.status !== 200) {
                output.innerText = "Eroare la citirea utilizatorilor.";
                return;
            }
            try {
                const utilizatori = JSON.parse(this.responseText);
                const gasit = utilizatori.find(u => u.utilizator === username);
                if (gasit && gasit.parola === password) {
                    output.innerText = "Utilizator și parolă corecte.";
                } else {
                    output.innerText = "Utilizator sau parolă incorecte.";
                }
            } catch (e) {
                output.innerText = "Eroare la parsarea JSON.";
            }
        }
    };
    xhttp.open("GET", "resurse/utilizatori.json", true);
    xhttp.send();
}

function inregistreazaUtilizator() {
    const utilizator = document.getElementById("uname").value;
    const parola = document.getElementById("pass").value;
    const out = document.getElementById("registerResult");

    const xhttp = new XMLHttpRequest();
    xhttp.onreadystatechange = function () {
        if (this.readyState === 4) {
            if (this.status === 200) {
                out.innerText = "Înregistrare reușită.";
            } else {
                out.innerText = "Eroare la înregistrare.";
            }
        }
    };

    xhttp.open("POST", "/api/utilizatori", true);
    xhttp.setRequestHeader("Content-Type", "application/json; charset=utf-8");
    xhttp.send(JSON.stringify({ utilizator, parola }));
}
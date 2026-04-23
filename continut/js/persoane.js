function incarcaPersoane() {
    var xhttp = new XMLHttpRequest();
    xhttp.onreadystatechange = function () {
        if (this.readyState == 4 && this.status == 200) {
            parseazaXML(this);
        } else if (this.readyState == 4) {
            afiseazaEroareIncarcare("Nu pot încărca persoanele (status " + this.status + ").");
        }
    };
    xhttp.open("GET", "resurse/persoane.xml", true);
    xhttp.send();
}

function parseazaXML(xml) {
    var xmlDoc = xml.responseXML;
    if (!xmlDoc) {
        try {
            xmlDoc = new DOMParser().parseFromString(xml.responseText, "application/xml");
        } catch (e) {
            xmlDoc = null;
        }
    }
    if (!xmlDoc || !xmlDoc.getElementsByTagName) {
        afiseazaEroareIncarcare("Răspuns XML invalid sau blocat de browser (ex. file://). Rulează proiectul printr-un server local.");
        return;
    }
    
    var table = "<table border='1' style='border-collapse: collapse; width: 100%; text-align: left;'>\n";
    table += "<tr><th>Nume</th><th>Prenume</th><th>Vârstă</th><th>Stradă</th><th>Număr</th><th>Localitate</th><th>Județ</th><th>Țară</th><th>Nivel Educație</th><th>Domeniu</th><th>Instituție</th><th>An</th><th>Ocupație</th></tr>\n";
    
    var persoane = xmlDoc.getElementsByTagName("persoana");
    
    for (var i = 0; i < persoane.length; i++) {
        table += "<tr>\n";
        
        table += "<td>" + persoane[i].getElementsByTagName("nume")[0].textContent + "</td>\n";
        table += "<td>" + persoane[i].getElementsByTagName("prenume")[0].textContent + "</td>\n";
        table += "<td>" + persoane[i].getElementsByTagName("varsta")[0].textContent + "</td>\n";
        
        table += "<td>" + persoane[i].getElementsByTagName("strada")[0].textContent + "</td>\n";
        table += "<td>" + persoane[i].getElementsByTagName("numar")[0].textContent + "</td>\n";
        table += "<td>" + persoane[i].getElementsByTagName("localitate")[0].textContent + "</td>\n";
        table += "<td>" + persoane[i].getElementsByTagName("judet")[0].textContent + "</td>\n";
        table += "<td>" + persoane[i].getElementsByTagName("tara")[0].textContent + "</td>\n";
        
        table += "<td>" + persoane[i].getElementsByTagName("nivel")[0].textContent + "</td>\n";
        table += "<td>" + persoane[i].getElementsByTagName("domeniu")[0].textContent + "</td>\n";
        table += "<td>" + persoane[i].getElementsByTagName("institutie")[0].textContent + "</td>\n";
        table += "<td>" + persoane[i].getElementsByTagName("an")[0].textContent + "</td>\n";
        table += "<td>" + persoane[i].getElementsByTagName("ocupatie")[0].textContent + "</td>\n";
        
        table += "</tr>\n";
    }
    
    table += "</table>";
    
    document.getElementById("loading").style.display = 'none';

    document.getElementById("tabelContainer").innerHTML = table;
}

function afiseazaEroareIncarcare(mesaj) {
    var loadingEl = document.getElementById("loading");
    if (loadingEl) {
        loadingEl.textContent = mesaj;
        loadingEl.style.display = 'block';
    }
    var container = document.getElementById("tabelContainer");
    if (container) container.innerHTML = "";
}
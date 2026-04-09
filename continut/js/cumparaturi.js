class Produs {
    constructor(name, quantity, id) {
        this.name = name;
        this.quantity = parseInt(quantity);
        this.id = id;
    }

    print() {
        console.log(this.name + ' ' + this.quantity)
    }

    increaseQuantity(nr) {
        this.quantity += nr;
    }
}

let shoppingList = [];

const myWorker = new Worker('js/worker.js');

myWorker.onmessage = (e) => {
    const produsPrimit = e.data;
    console.log("Confirmare pentru: " + produsPrimit.name);

    renderTable();
};

const addProduct = () => {
    const name = document.getElementById("produse").value;
    const quantity = parseInt(document.getElementById("cantitate").value);

    let existentProduct = shoppingList.find(p => p.name === name);

    let currentProduct;

    if (existentProduct) {
        existentProduct.increaseQuantity(quantity);
        currentProduct = existentProduct;
    }
    else {
        const id = shoppingList.length + 1;
        currentProduct = new Produs(name, quantity, id);
        shoppingList.push(currentProduct);
    }

    localStorage.setItem(`produs_${currentProduct.id}`, JSON.stringify(currentProduct));

    new Promise((resolve) => {
        myWorker.postMessage(currentProduct);
        resolve();
    }).then(() => console.log("Mesaj trimis catre worker prin Promise"));
}

const renderTable = () => {
    const tbody = document.getElementById("corp-tabel");

    tbody.innerHTML = "";

    shoppingList.forEach(p => {
        const row = `<tr>
            <td>${p.id}</td>
            <td>${p.name}</td>
            <td>${p.quantity}</td>
        </tr>`;

        tbody.innerHTML += row;
    });
};
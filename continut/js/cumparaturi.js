class Produs {
    constructor(name, quantity, id) {
        this.name = name;
        this.quantity = quantity;
        this.id = id;
    }

    print() {
        console.log(this.name + ' ' + this.quantity)
    }

    increaseQuantity(nr) {
        this.quantity += nr;
    }
}

const manusi = new Produs("manusiDeBox", 0, 1);
const sac = new Produs("sacDeBox", 0, 2);
const proteza = new Produs("proteza", 0, 3);
const bandaje = new Produs("bandaje", 0, 4);
const casca = new Produs("casca", 0, 5);

function printAll() {
    manusi.print();
    sac.print();
    proteza.print();
    bandaje.print();
    casca.print();
}

function addProduct() {
    let productName = document.getElementById("produse").value;
    let productQuantity = document.getElementById("cantitate").value;

    localStorage.setItem(productName, productQuantity);

    switch(productName) {
        case "manusiDeBox":
            manusi.increaseQuantity(productQuantity);
            break;
        case "sacDeBox":
            sac.increaseQuantity(productQuantity);
            break;
        case "proteza":
            proteza.increaseQuantity(productQuantity);
            break;
        case "bandaje":
            bandaje.increaseQuantity(productQuantity);
            break;
        case "casca":
            casca.increaseQuantity(productQuantity);
            break;
        default:
            break;
    }
}

function test() {
    let productName = document.getElementById("produse").value;

    console.log(localStorage.getItem(productName));
}
self.onmessage = function(e) {
    const produs = e.data;

    console.log("Worker-ul adaugă produsul: " + produs.name);

    self.postMessage(produs);
}
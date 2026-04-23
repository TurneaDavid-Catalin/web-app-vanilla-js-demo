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

class ShoppingStorage {
    async loadAll() {
        throw new Error('Not implemented');
    }

    async upsert(produs) {
        throw new Error('Not implemented');
    }

    async clear() {
        throw new Error('Not implemented');
    }
}

class LocalStorageShoppingStorage extends ShoppingStorage {
    constructor(prefix = 'produs_') {
        super();
        this.prefix = prefix;
    }

    async loadAll() {
        const items = [];
        for (let i = 0; i < localStorage.length; i++) {
            const key = localStorage.key(i);
            if (!key || !key.startsWith(this.prefix)) continue;
            try {
                const val = localStorage.getItem(key);
                if (!val) continue;
                const parsed = JSON.parse(val);
                if (!parsed || typeof parsed !== 'object') continue;

                const id = Number(parsed.id);
                const name = typeof parsed.name === 'string' ? parsed.name : undefined;
                const quantity = Number(parsed.quantity);

                if (!Number.isFinite(id) || id <= 0) continue;
                if (!name) continue;
                if (!Number.isFinite(quantity)) continue;

                items.push({ id, name, quantity });
            } catch (_) {
                // ignore corrupt entries
            }
        }
        items.sort((a, b) => (a.id ?? 0) - (b.id ?? 0));
        return items;
    }

    async upsert(produs) {
        localStorage.setItem(`${this.prefix}${produs.id}`, JSON.stringify(produs));
    }

    async clear() {
        const toDelete = [];
        for (let i = 0; i < localStorage.length; i++) {
            const key = localStorage.key(i);
            if (key && key.startsWith(this.prefix)) toDelete.push(key);
        }
        toDelete.forEach((k) => localStorage.removeItem(k));
    }
}

class IndexedDBShoppingStorage extends ShoppingStorage {
    constructor(dbName = 'shopping_db', storeName = 'products') {
        super();
        this.dbName = dbName;
        this.storeName = storeName;
    }

    async _open() {
        return await new Promise((resolve, reject) => {
            const req = indexedDB.open(this.dbName, 1);
            req.onupgradeneeded = () => {
                const db = req.result;
                if (!db.objectStoreNames.contains(this.storeName)) {
                    db.createObjectStore(this.storeName, { keyPath: 'id' });
                }
            };
            req.onsuccess = () => resolve(req.result);
            req.onerror = () => reject(req.error);
        });
    }

    async loadAll() {
        const db = await this._open();
        try {
            return await new Promise((resolve, reject) => {
                const tx = db.transaction(this.storeName, 'readonly');
                const store = tx.objectStore(this.storeName);
                const req = store.getAll();
                req.onsuccess = () => {
                    const res = req.result ?? [];
                    res.sort((a, b) => (a.id ?? 0) - (b.id ?? 0));
                    resolve(res);
                };
                req.onerror = () => reject(req.error);
            });
        } finally {
            db.close();
        }
    }

    async upsert(produs) {
        const db = await this._open();
        try {
            await new Promise((resolve, reject) => {
                const tx = db.transaction(this.storeName, 'readwrite');
                const store = tx.objectStore(this.storeName);
                const req = store.put(produs);
                req.onsuccess = () => resolve();
                req.onerror = () => reject(req.error);
            });
        } finally {
            db.close();
        }
    }

    async clear() {
        const db = await this._open();
        try {
            await new Promise((resolve, reject) => {
                const tx = db.transaction(this.storeName, 'readwrite');
                const store = tx.objectStore(this.storeName);
                const req = store.clear();
                req.onsuccess = () => resolve();
                req.onerror = () => reject(req.error);
            });
        } finally {
            db.close();
        }
    }
}

let storageMode = localStorage.getItem('shopping_storage_mode') || 'localStorage';
let storageProvider = null;

const _createProvider = (mode) => {
    if (mode === 'indexedDB') return new IndexedDBShoppingStorage();
    return new LocalStorageShoppingStorage();
};

const _syncModeUI = () => {
    const sel = document.getElementById('storage-mode');
    if (!sel) return;
    sel.value = storageMode;
};

const _reloadFromStorage = async () => {
    if (!storageProvider) storageProvider = _createProvider(storageMode);
    const raw = await storageProvider.loadAll();
    // reconstruim instante Produs (optional, dar mentinem metoda increaseQuantity)
    shoppingList = raw
        .map((p) => {
            if (!p) return null;
            if (p.name == null || p.quantity == null || p.id == null) return null;
            return new Produs(p.name, p.quantity, p.id);
        })
        .filter(Boolean);
    renderTable();
};

const setStorageMode = async (mode) => {
    storageMode = mode;
    localStorage.setItem('shopping_storage_mode', storageMode);
    storageProvider = _createProvider(storageMode);
    await _reloadFromStorage();
};

const initCumparaturi = async () => {
    storageProvider = _createProvider(storageMode);
    _syncModeUI();
    await _reloadFromStorage();
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

    if (!storageProvider) storageProvider = _createProvider(storageMode);
    storageProvider.upsert(currentProduct);

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
import socket
import os
import threading
import gzip
from io import BytesIO
import json
from urllib.parse import unquote, parse_qs
# creeaza un server socket
serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# specifica ca serverul va rula pe portul 5678, accesibil de pe orice ip al
# serverului
serversocket.bind(('', 5678))
# serverul poate accepta conexiuni; specifica cati clienti pot astepta la coada
serversocket.listen(5) 

CONTENT_TYPES = {
    'html': 'text/html; charset=utf-8',
    'css': 'text/css; charset=utf-8',
    'js': 'application/js; charset=utf-8',
    'png': 'text/png',
    'jpg': 'text/jpeg',
    'jpeg': 'text/jpeg',
    'gif': 'text/gif',
    'ico': 'image/x-icon',
}

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'continut'))


def _safe_join(base_dir: str, url_path: str) -> str | None:
    # Elimina query string si decodeaza %xx
    path_only = url_path.split('?', 1)[0].split('#', 1)[0]
    path_only = unquote(path_only)

    if path_only in ('', '/'):
        path_only = '/index.html'
    elif not os.path.splitext(path_only)[1]:
        # pentru rute de forma /despre => despre.html (compatibil cu cerintele anterioare)
        path_only = f'{path_only}.html'

    # normalizeaza si previne path traversal (../)
    candidate = os.path.abspath(os.path.join(base_dir, path_only.lstrip('/')))
    if os.path.commonpath([base_dir, candidate]) != base_dir:
        return None
    return candidate


def _content_type_for(path: str) -> str:
    ext = os.path.splitext(path)[1].lstrip('.').lower()
    return CONTENT_TYPES.get(ext, 'application/octet-stream')


def _http_response(status_line: str, headers: dict[str, str], body: bytes) -> bytes:
    lines = [status_line]
    for k, v in headers.items():
        lines.append(f'{k}: {v}')
    head = '\r\n'.join(lines).encode('utf-8') + b'\r\n\r\n'
    return head + body


def _gzip_bytes(data: bytes) -> bytes:
    buf = BytesIO()
    with gzip.GzipFile(fileobj=buf, mode='wb') as gz:
        gz.write(data)
    return buf.getvalue()


def _read_http_request(clientsocket: socket.socket) -> tuple[str, dict[str, str], bytes]:
    # Citim pana la sfarsitul headerelor: \r\n\r\n
    raw = b''
    while b'\r\n\r\n' not in raw:
        chunk = clientsocket.recv(1024)
        if not chunk:
            break
        raw += chunk

    head_bytes, sep, rest = raw.partition(b'\r\n\r\n')
    text = head_bytes.decode('iso-8859-1', errors='replace')
    lines = text.split('\r\n')
    start_line = lines[0] if lines else ''
    headers: dict[str, str] = {}
    for line in lines[1:]:
        if not line or ':' not in line:
            continue
        k, v = line.split(':', 1)
        headers[k.strip().lower()] = v.strip()

    content_length = 0
    try:
        content_length = int(headers.get('content-length', '0'))
    except Exception:
        content_length = 0

    body = rest
    while len(body) < content_length:
        chunk = clientsocket.recv(1024)
        if not chunk:
            break
        body += chunk
    if content_length >= 0:
        body = body[:content_length]

    return start_line, headers, body


def _json_response(status_line: str, obj, client_accepts_gzip: bool) -> bytes:
    body = json.dumps(obj, ensure_ascii=False).encode('utf-8')
    headers = {
        'Content-Type': 'application/json; charset=utf-8',
        'Server': 'server',
    }
    if client_accepts_gzip:
        body = _gzip_bytes(body)
        headers['Content-Encoding'] = 'gzip'
    headers['Content-Length'] = str(len(body))
    return _http_response(status_line, headers, body)


def _handle_client(clientsocket: socket.socket, address):
    try:
        print('S-a conectat un client.')

        linieDeStart, req_headers, req_body = _read_http_request(clientsocket)
        print('S-a citit linia de start din cerere: ##### ' + linieDeStart + '#####')

        parts = linieDeStart.split()
        method = parts[0] if len(parts) > 0 else ''
        resursaCeruta = parts[1] if len(parts) > 1 else '/'
        # normalizare pentru rutare (fara query/fragment, fara trailing slash)
        ruta = resursaCeruta.split('?', 1)[0].split('#', 1)[0]
        if ruta != '/' and ruta.endswith('/'):
            ruta = ruta.rstrip('/')

        accept_encoding = req_headers.get('accept-encoding', '')
        client_accepts_gzip = 'gzip' in accept_encoding.lower()

        # Ruta speciala: /api/utilizatori (nu exista fisier, e procesare)
        if ruta == '/api/utilizatori' and method.upper() == 'OPTIONS':
            # raspuns minimal pentru preflight / testare
            body = b''
            headers = {
                'Content-Length': '0',
                'Server': 'server',
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'POST, OPTIONS',
                'Access-Control-Allow-Headers': 'Content-Type',
            }
            clientsocket.sendall(_http_response('HTTP/1.1 204 No Content', headers, body))
            return

        if ruta == '/api/utilizatori' and method.upper() == 'POST':
            content_type = req_headers.get('content-type', '').lower()
            payload = None
            try:
                if 'application/json' in content_type:
                    payload = json.loads(req_body.decode('utf-8', errors='replace'))
                elif 'application/x-www-form-urlencoded' in content_type:
                    form = parse_qs(req_body.decode('utf-8', errors='replace'), keep_blank_values=True)
                    payload = {
                        'utilizator': (form.get('utilizator') or form.get('uname') or [''])[0],
                        'parola': (form.get('parola') or form.get('pass') or [''])[0],
                    }
                else:
                    # fallback: incercam JSON
                    payload = json.loads(req_body.decode('utf-8', errors='replace'))
            except Exception:
                payload = None

            if not payload or not payload.get('utilizator') or not payload.get('parola'):
                clientsocket.sendall(_json_response('HTTP/1.1 400 Bad Request', {'ok': False, 'error': 'Date invalide'}, client_accepts_gzip))
                return

            utilizator = str(payload['utilizator'])
            parola = str(payload['parola'])

            users_path = os.path.join(BASE_DIR, 'resurse', 'utilizatori.json')
            try:
                if os.path.exists(users_path):
                    with open(users_path, 'rb') as f:
                        existing = json.loads(f.read().decode('utf-8', errors='replace') or '[]')
                else:
                    existing = []
            except Exception:
                existing = []

            if not isinstance(existing, list):
                existing = []

            updated = False
            for u in existing:
                if isinstance(u, dict) and u.get('utilizator') == utilizator:
                    u['parola'] = parola
                    updated = True
                    break
            if not updated:
                existing.append({'utilizator': utilizator, 'parola': parola})

            with open(users_path, 'wb') as f:
                f.write(json.dumps(existing, ensure_ascii=False, indent=2).encode('utf-8'))

            clientsocket.sendall(_json_response('HTTP/1.1 200 OK', {'ok': True, 'updated': updated}, client_accepts_gzip))
            return

        if method.upper() != 'GET':
            body = 'Method Not Allowed'.encode('utf-8')
            headers = {
                'Content-Type': 'text/plain; charset=utf-8',
                'Server': 'server',
            }
            if client_accepts_gzip:
                body = _gzip_bytes(body)
                headers['Content-Encoding'] = 'gzip'
            headers['Content-Length'] = str(len(body))
            response = _http_response('HTTP/1.1 405 Method Not Allowed', headers, body)
            clientsocket.sendall(response)
            return

        file_path = _safe_join(BASE_DIR, ruta)
        if file_path is None or not os.path.exists(file_path) or not os.path.isfile(file_path):
            body = b'<html><body><h1>404 Not Found</h1></body></html>'
            headers = {
                'Content-Type': 'text/html; charset=utf-8',
                'Server': 'server',
            }
            if client_accepts_gzip:
                body = _gzip_bytes(body)
                headers['Content-Encoding'] = 'gzip'
            headers['Content-Length'] = str(len(body))
            response = _http_response('HTTP/1.1 404 Not Found', headers, body)
            clientsocket.sendall(response)
            return

        with open(file_path, 'rb') as f:
            body = f.read()

        headers = {
            'Content-Type': _content_type_for(file_path),
            'Server': 'server',
        }

        if client_accepts_gzip:
            body = _gzip_bytes(body)
            headers['Content-Encoding'] = 'gzip'

        headers['Content-Length'] = str(len(body))
        response = _http_response('HTTP/1.1 200 OK', headers, body)
        clientsocket.sendall(response)
    except Exception as e:
        body = f'Internal Server Error\n{e}'.encode('utf-8')
        headers = {
            'Content-Type': 'text/plain; charset=utf-8',
            'Server': 'server',
        }
        # gzip optional si aici (daca apare eroare dupa ce am citit headerul)
        try:
            if 'req_headers' in locals():
                accept_encoding = req_headers.get('accept-encoding', '')
                if 'gzip' in accept_encoding.lower():
                    body = _gzip_bytes(body)
                    headers['Content-Encoding'] = 'gzip'
        except Exception:
            pass
        headers['Content-Length'] = str(len(body))
        response = _http_response('HTTP/1.1 500 Internal Server Error', headers, body)
        clientsocket.sendall(response)
    finally:
        clientsocket.close()
        print('S-a terminat comunicarea cu clientul.')


while True:
    print('#########################################################################')
    print('Serverul asculta potentiali clienti.')
    # asteapta conectarea unui client la server
    # metoda `accept` este blocanta => clientsocket, care reprezinta socket-ul
    # corespunzator clientului conectat
    (clientsocket, address) = serversocket.accept()
    threading.Thread(target=_handle_client, args=(clientsocket, address), daemon=True).start()
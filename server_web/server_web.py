import socket
import os
import threading
import gzip
from io import BytesIO
from urllib.parse import unquote
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


def _read_http_request(clientsocket: socket.socket) -> tuple[str, dict[str, str]]:
    # Citim pana la sfarsitul headerelor: \r\n\r\n
    raw = b''
    while b'\r\n\r\n' not in raw:
        chunk = clientsocket.recv(1024)
        if not chunk:
            break
        raw += chunk

    # Header-ele HTTP sunt definite ca ISO-8859-1 pentru mapping 1:1 bytes->chars.
    text = raw.decode('iso-8859-1', errors='replace')
    header_part = text.split('\r\n\r\n', 1)[0]
    lines = header_part.split('\r\n')
    start_line = lines[0] if lines else ''
    headers: dict[str, str] = {}
    for line in lines[1:]:
        if not line or ':' not in line:
            continue
        k, v = line.split(':', 1)
        headers[k.strip().lower()] = v.strip()
    return start_line, headers


def _handle_client(clientsocket: socket.socket, address):
    try:
        print('S-a conectat un client.')

        linieDeStart, req_headers = _read_http_request(clientsocket)
        print('S-a citit linia de start din cerere: ##### ' + linieDeStart + '#####')

        parts = linieDeStart.split()
        method = parts[0] if len(parts) > 0 else ''
        resursaCeruta = parts[1] if len(parts) > 1 else '/'

        accept_encoding = req_headers.get('accept-encoding', '')
        client_accepts_gzip = 'gzip' in accept_encoding.lower()

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

        file_path = _safe_join(BASE_DIR, resursaCeruta)
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
import socket
import os
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


while True:
    print('#########################################################################')
    print('Serverul asculta potentiali clienti.')
    # asteapta conectarea unui client la server
    # metoda `accept` este blocanta => clientsocket, care reprezinta socket-ul
    # corespunzator clientului conectat
    (clientsocket, address) = serversocket.accept()
    print('S-a conectat un client.')
    # se proceseaza cererea si se citeste prima linie de text
    cerere = ''
    linieDeStart = ''
    while True:
        data = clientsocket.recv(1024)
        cerere = cerere + data.decode()
        print('S-a citit mesajul: \n---------------------------\n' + cerere + '\n---------------------------')
        pozitie = cerere.find('\r\n')
        if (pozitie > -1):
            linieDeStart = cerere[0:pozitie]
            print('S-a citit linia de start din cerere: ##### ' + linieDeStart + '#####')
            break
    print('S-a terminat cititrea.')
    try:
        parts = linieDeStart.split()
        method = parts[0] if len(parts) > 0 else ''
        resursaCeruta = parts[1] if len(parts) > 1 else '/'

        if method.upper() != 'GET':
            body = b'Method Not Allowed'
            response = _http_response(
                'HTTP/1.1 405 Method Not Allowed',
                {
                    'Content-Length': str(len(body)),
                    'Content-Type': 'text/plain; charset=utf-8',
                    'Server': 'server',
                },
                body,
            )
            clientsocket.sendall(response)
        else:
            file_path = _safe_join(BASE_DIR, resursaCeruta)
            if file_path is None or not os.path.exists(file_path) or not os.path.isfile(file_path):
                body = b'<html><body><h1>404 Not Found</h1></body></html>'
                response = _http_response(
                    'HTTP/1.1 404 Not Found',
                    {
                        'Content-Length': str(len(body)),
                        'Content-Type': 'text/html; charset=utf-8',
                        'Server': 'server',
                    },
                    body,
                )
                clientsocket.sendall(response)
            else:
                with open(file_path, 'rb') as f:
                    body = f.read()
                response = _http_response(
                    'HTTP/1.1 200 OK',
                    {
                        'Content-Length': str(len(body)),
                        'Content-Type': _content_type_for(file_path),
                        'Server': 'server',
                    },
                    body,
                )
                clientsocket.sendall(response)
    except Exception as e:
        body = f'Internal Server Error\n{e}'.encode('utf-8')
        response = _http_response(
            'HTTP/1.1 500 Internal Server Error',
            {
                'Content-Length': str(len(body)),
                'Content-Type': 'text/plain; charset=utf-8',
                'Server': 'server',
            },
            body,
        )
        clientsocket.sendall(response)

    clientsocket.close()
    print('S-a terminat comunicarea cu clientul.')
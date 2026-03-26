import socket
# creeaza un server socket
serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# specifica ca serverul va rula pe portul 5678, accesibil de pe orice ip al
# serverului
serversocket.bind(('', 5678))
# serverul poate accepta conexiuni; specifica cati clienti pot astepta la coada
serversocket.listen(5) 
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
    # TODO interpretarea sirului de caractere `linieDeStart` pentru a extrage
    #numele resursei cerute
    #GET /index.html HTTP/1.1
    extensiiValide = ['html']
    resurseHtmlValide = ['/desen', '/despre', '/index', '/inregistreaza', '/invat']

    resursaCeruta = linieDeStart.split()[1]

    resursaCerutaNume = resursaCeruta.split('.')[0]
    resursaCerutaExtensie = resursaCeruta.split('.')[1]

    if resursaCerutaExtensie in extensiiValide:
        if resursaCerutaNume in resurseHtmlValide:
            htmlResponse = 'HTTP/1.1 200 OK\r\n'
        else:
            htmlResponse = 'HTTP/1.1 404 Not Found\r\n'
    
    mesaj = 'Hello World! - ' + resursaCeruta

    htmlResponse += 'Content-Length: ' + str(len(mesaj.encode('utf-8'))) + '\r\n'
    htmlResponse += 'Content-Type: text/plain' + '\r\n'
    htmlResponse += 'Server: server' + '\r\n'
    htmlResponse += '\r\n'
    htmlResponse += mesaj
    
    print(htmlResponse)

    clientsocket.sendall(htmlResponse.encode('utf-8'))

    # TODO trimiterea răspunsului HTTP

    clientsocket.close()
    print('S-a terminat comunicarea cu clientul.')

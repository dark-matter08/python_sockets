import socket
import select

HEADER_LENGTH = 10
IP = "127.0.0.1"
PORT = 1234

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

server_socket.bind((IP, PORT))

server_socket.listen()
print(f"Listening for connections on {IP}:{PORT}...")

sockets_list = [server_socket]

clients = {}

def recieve_message(client_socket):
    try:
        message_header = client_socket.recv(HEADER_LENGTH)

        if not len(message_header):
            return False
        
        message_length = int(message_header.decode("utf-8").strip())
        return {"header": message_header, "data":client_socket.recv(message_length)}
    
    except:
        return False


while True:
    read_sockets, _, exception_sockets = select.select(sockets_list, [], sockets_list)

    for notified_sockets in read_sockets:
        if notified_sockets ==  server_socket:
            client_socket, client_address =  server_socket.accept()
            user = recieve_message(client_socket)

            if user is False:
                continue

            sockets_list.append(client_socket)
            clients[client_socket] = user

            print(f"Accepted new connection from {client_address[0]}:{client_address[1]} username: {user['data'].decode('utf-8')}")

        else:
            message =  recieve_message(notified_sockets)

            if message is False:
                print('Closed connection from: {}'.format(clients[notified_sockets]['data'].decode('utf-8')))
                sockets_list.remove(notified_sockets)
                del clients[notified_sockets]
                continue

            user = clients[notified_sockets]
            username_rec = user['data'].decode('utf-8')
            print(f"Recieved message from {user['data'].decode('utf-8')}: {message['data'].decode('utf-8')}")


            for client_socket in clients:
                if client_socket != notified_sockets:
                    client_socket.send(user['header'] + user['data'] + message['header'] + message['data'])

    
    for notfied_sockets in exception_sockets:
        sockets_list.remove(notfied_sockets)

        del clients[notfied_sockets]







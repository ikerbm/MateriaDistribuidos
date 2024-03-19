import socket
import threading

def handle_client(client_socket, addr):
    while True:
        try:
            data = client_socket.recv(1024)
            if not data:
                break
            print(f"Mensaje recibido de {addr}: {data.decode('utf-8')}")
            response = input("Ingrese su respuesta: ")
            client_socket.sendall(response.encode('utf-8'))
        except ConnectionResetError:
            break
    client_socket.close()

def start_server(host, port):
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((host, port))
    server.listen(5)
    print(f"[*] Escuchando en {host}:{port}")

    while True:
        client_sock, addr = server.accept()
        print(f"[*] Conexión establecida desde {addr[0]}:{addr[1]}")
        client_handler = threading.Thread(target=handle_client, args=(client_sock, addr))
        client_handler.start()

def connect_to_peers(peer_list):
    while True:
        for peer in peer_list:
            client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            try:
                client.connect(peer)
                print(f"[+] Conectado a {peer[0]}:{peer[1]}")
                while True:
                    message = input("Ingrese un mensaje para el servidor: ")
                    client.sendall(message.encode('utf-8'))
                    response = client.recv(1024)
                    print(f"Respuesta del servidor: {response.decode('utf-8')}")
                    continuar = input("¿Desea enviar otro mensaje? (s/n): ")
                    if continuar.lower() != 's':
                        break
            except ConnectionRefusedError:
                print(f"[-] No se pudo conectar a {peer[0]}:{peer[1]}")
            finally:
                client.close()

if __name__ == "__main__":
    host = '10.253.32.237'  # Dirección IPv4 del servidor
    port = 12345  # Puerto arbitrario

    # Definir la lista de peers (dirección y puerto de cada computadora)
    peer_list = [
        ('10.253.51.229', port),  # Dirección IPv4 del primer peer
        ('192.168.202.65', port),  # Dirección IPv4 del segundo peer
        ('192.168.202.66', port)   # Dirección IPv4 del tercer peer
        # Agregar más peers según sea necesario
    ]

    # Iniciar el servidor en un hilo separado
    server_thread = threading.Thread(target=start_server, args=(host, port))
    server_thread.start()

    # Conectar a los peers
    connect_to_peers(peer_list)

import socket
import threading

# Configuración de red
host = '192.168.202.92'  # Dirección IPv4 del servidor
port = 12345  # Puerto arbitrario

# Lista para almacenar los sockets de los clientes
clientes_conectados = []

# Función para manejar la conexión de un cliente
def handle_client(client_socket, client_address):
    print(f"Conexión establecida desde: {client_address}")

    # Agregar el socket del cliente a la lista de clientes conectados
    clientes_conectados.append(client_socket)

    while True:
        # Recibir datos del cliente
        data = client_socket.recv(1024)
        if not data:
            break

        # Imprimir el mensaje del cliente
        print(f"Mensaje del cliente {client_address}: {data.decode('utf-8')}")

        # Enviar el mensaje a todos los clientes excepto al que lo envió
        for cliente in clientes_conectados:
            if cliente != client_socket:
                try:
                    cliente.sendall(data)
                    
                except:
                    # En caso de error al enviar el mensaje, eliminar el cliente de la lista
                    clientes_conectados.remove(cliente)

    print(f"Conexión cerrada desde: {client_address}")
    client_socket.close()

# Crear un socket TCP/IP
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Enlace del socket a la dirección y puerto
sock.bind((host, port))

# Escuchar conexiones entrantes
sock.listen(5)
print(f"Servidor escuchando en {host}:{port}")

while True:
    # Aceptar la conexión del cliente
    client_socket, client_address = sock.accept()

    # Crear un hilo para manejar la conexión del cliente
    client_thread = threading.Thread(target=handle_client, args=(client_socket, client_address))
    client_thread.start()

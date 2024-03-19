import socket
import threading

# Función para manejar la recepción de mensajes del servidor
def receive_messages(sock):
    while True:
        try:
            # Recibir datos del servidor
            data = sock.recv(1024)
            if not data:
                break
            # Imprimir el mensaje recibido del servidor
            print(f"Respuesta del servidor: {data.decode('utf-8')}")
        except:
            break

# Configuración de red
host = '192.168.202.81'  # Dirección IPv4 del servidor
port = 12345  # Puerto arbitrario

# Crear un socket TCP/IP
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Conectar el socket al servidor remoto
sock.connect((host, port))

# Crear un hilo para manejar la recepción de mensajes del servidor
receive_thread = threading.Thread(target=receive_messages, args=(sock,))
receive_thread.start()

# Enviar y recibir mensajes con el servidor
while True:
    # Permitir al usuario enviar un mensaje al servidor
    message = input(" ")
    sock.sendall(message.encode('utf-8'))


# Cerrar la conexión
sock.close()

import socket

# Configuración de red
host = '192.168.202.63'  # Dirección IPv4 del servidor
port = 12345  # Puerto arbitrario

# Crear un socket TCP/IP
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Conectar el socket al servidor remoto
sock.connect((host, port))

while True:
    # Enviar datos al servidor
    message = input("Ingrese un mensaje para el servidor: ")
    sock.sendall(message.encode('utf-8'))

    # Recibir respuesta del servidor
    data = sock.recv(1024)
    print(f"Respuesta del servidor: {data.decode('utf-8')}")

    # Preguntar al usuario si desea enviar otro mensaje
    continuar = input("¿Desea enviar otro mensaje? (s/n): ")
    if continuar.lower() != 's':
        break

# Cerrar la conexión
sock.close()

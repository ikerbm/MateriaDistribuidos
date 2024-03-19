import socket
import threading
import tkinter as tk
from tkinter import scrolledtext, messagebox

# Definir variables globales
PORT = 9998  # Puerto para la comunicación
BUFFER_SIZE = 1024  # Tamaño del búfer para recibir datos

# Lista para almacenar los sockets de los clientes conectados
connected_peers_sockets = []

# Función para manejar la conexión con un cliente
def handle_peer_connection(peer_socket, chat_box):
    try:
        # Bucle para recibir mensajes del cliente
        while True:
            message = peer_socket.recv(BUFFER_SIZE).decode('utf-8')  # Recibir mensaje
            if not message:  # Si no hay mensaje, salir del bucle
                break
            chat_box.insert(tk.END, '' + message + '\n')  # Mostrar mensaje en el chatbox
    except Exception as e:
        print(f"Error: {e}")
    finally:
        peer_socket.close()  # Cerrar el socket del cliente
        connected_peers_sockets.remove(peer_socket)  # Eliminar el socket de la lista de conexiones

# Función para enviar un mensaje a los destinatarios
def send_message(client_name, message_entry, dest_ip_entry):
    message = message_entry.get()  # Obtener el mensaje del usuario
    dest_ips = dest_ip_entry.get().split(',')  # Obtener las direcciones IP de los destinatarios
    for dest_ip in dest_ips:
        dest_ip = dest_ip.strip()  # Eliminar espacios en blanco alrededor de la dirección IP
        if message and dest_ip:  # Verificar que haya un mensaje y una dirección IP válida
            try:
                # Crear un socket y conectarse al destinatario
                dest_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                dest_socket.connect((dest_ip, PORT))
                # Enviar el mensaje al destinatario
                dest_socket.send(f"Mensaje de {client_name}: {message}".encode('utf-8'))
                dest_socket.close()  # Cerrar el socket
                message_entry.delete(0, tk.END)  # Limpiar la entrada del mensaje
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo conectar con {dest_ip}: {e}")
        else:
            messagebox.showerror("Error", "Por favor ingrese un mensaje y una dirección IP válida.")

# Función para configurar la interfaz gráfica del cliente
def client_start(root, chat_box, client_name):
    dest_ip_label = tk.Label(root, text="IP Destinatario:")
    dest_ip_label.pack()
    dest_ip_entry = tk.Entry(root, width=30)
    dest_ip_entry.pack()

    message_label = tk.Label(root, text="Mensaje:")
    message_label.pack()
    message_entry = tk.Entry(root, width=50)
    message_entry.pack()

    # Botón para enviar mensajes
    send_button = tk.Button(root, text="Enviar", command=lambda: send_message(client_name, message_entry, dest_ip_entry))
    send_button.pack()

# Función para iniciar el servidor
def server_start(chat_box):
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(('0.0.0.0', PORT))  # Enlazar el servidor al puerto
    server.listen(5)  # Escuchar hasta 5 conexiones entrantes

    while True:
        client, addr = server.accept()  # Aceptar nueva conexión
        print(f"Accepted connection from: {addr[0]}:{addr[1]}")
        connected_peers_sockets.append(client)  # Agregar el socket del cliente a la lista
        # Crear un hilo para manejar la conexión con el cliente
        client_handler = threading.Thread(target=handle_peer_connection, args=(client, chat_box))
        client_handler.start()

if __name__ == "__main__":
    # Configurar la ventana principal de Tkinter
    root = tk.Tk()
    root.title("Chat")

    # Configurar un área de texto para mostrar los mensajes del chat
    frame = tk.Frame(root)
    scrollbar = tk.Scrollbar(frame)
    chat_box = scrolledtext.ScrolledText(frame, height=15, width=50, yscrollcommand=scrollbar.set)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    chat_box.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    frame.pack()

    # Solicitar al usuario que ingrese su nombre de usuario
    client_name = input("Ingresa tu nombre de usuario: ")

    # Iniciar un hilo para el servidor
    server_thread = threading.Thread(target=server_start, args=(chat_box,))
    server_thread.start()

    # Configurar la interfaz gráfica del cliente
    client_start(root, chat_box, client_name)

    # Iniciar el bucle principal de Tkinter
    root.mainloop()
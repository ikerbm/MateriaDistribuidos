import socket
import threading
import tkinter as tk
from tkinter import scrolledtext

PORT = 9998
BUFFER_SIZE = 1024

connected_peers_sockets = []

def handle_peer_connection(peer_socket, chat_box):
    try:
        while True:
            message = peer_socket.recv(BUFFER_SIZE).decode('utf-8')
            if not message:
                break
            chat_box.insert(tk.END, 'Mensaje recibido: ' + message + '\n')
    except Exception as e:
        print(f"Error: {e}")
    finally:
        peer_socket.close()
        connected_peers_sockets.remove(peer_socket)

def send_message(event=None, client_name='', message_entry=None):
    message = message_entry.get()
    if message:
        for peer_socket in connected_peers_sockets:
            peer_socket.send(f"Mensaje de {client_name}: {message}".encode('utf-8'))
        message_entry.delete(0, tk.END)

def client_start(root, chat_box, client_name):
    message_entry = tk.Entry(root, width=50)
    message_entry.bind("<Return>", lambda event: send_message(event, client_name, message_entry))
    message_entry.pack()

    send_button = tk.Button(root, text="Enviar", command=lambda: send_message(None, client_name, message_entry))
    send_button.pack()

def server_start(chat_box):
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(('0.0.0.0', PORT))
    server.listen(5)

    while True:
        client, addr = server.accept()
        print(f"Accepted connection from: {addr[0]}:{addr[1]}")
        connected_peers_sockets.append(client)
        client_handler = threading.Thread(target=handle_peer_connection, args=(client, chat_box))
        client_handler.start()

if __name__ == "__main__":
    root = tk.Tk()
    root.title("Chat")

    frame = tk.Frame(root)
    scrollbar = tk.Scrollbar(frame)
    chat_box = scrolledtext.ScrolledText(frame, height=15, width=50, yscrollcommand=scrollbar.set)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    chat_box.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    frame.pack()

    client_name = input("Ingresa tu nombre de usuario: ")

    server_thread = threading.Thread(target=server_start, args=(chat_box,))
    server_thread.start()

    client_start(root, chat_box, client_name)

    root.mainloop()
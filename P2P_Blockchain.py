import json
import socket
import threading
import tkinter as tk
import hashlib
from time import time
from tkinter import messagebox
import pickle

BUFFER_SIZE = 1024  # Tamaño del buffer para la transferencia de datos
PORT = 5555  # Puerto para la conexión de red
connected_peers_sockets = []  # Lista de sockets de pares conectados

class Blockchain:
    def __init__(self):
        self.chain = []  # Cadena de bloques
        self.current_transactions = []  # Transacciones actuales
        self.difficulty = 4  # Dificultad para la prueba de trabajo
        self.create_genesis_block()  # Crear el bloque génesis al inicializar la cadena de bloques

    def create_genesis_block(self):
        # Crea el bloque génesis, el primer bloque en la cadena de bloques
        genesis_block = {
            'index': 0,
            'timestamp': time(),
            'transactions': [],
            'previous_hash': '0' * 64,
            'nonce': 0
        }
        genesis_block['hash'] = self.hash(genesis_block)
        self.chain.append(genesis_block)

    def hash(self, block):
        # Calcula el hash SHA-256 de un bloque
        encoded_block = json.dumps(self.remove_bytes(block), sort_keys=True).encode()
        return hashlib.sha256(encoded_block).hexdigest()

    def remove_bytes(self, obj):
        # Elimina los bytes de un objeto para poder calcular su hash
        if isinstance(obj, dict):
            return {k: self.remove_bytes(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [self.remove_bytes(item) for item in obj]
        elif isinstance(obj, bytes):
            return obj.decode()
        else:
            return obj

    def mine_block(self, transactions):
        # Minar un bloque con las transacciones dadas
        last_block = self.chain[-1]
        nonce = 0
        while True:
            block = {
                'index': len(self.chain),
                'timestamp': time(),
                'transactions': transactions,
                'previous_hash': last_block['hash'],
                'nonce': nonce
            }
            block_hash = self.hash(block)
            if block_hash.startswith('0' * self.difficulty):
                break
            nonce += 1
        self.chain.append(block)
        self.current_transactions = []
        return block

    def sync_blockchain(self, blockchain):
        # Sincroniza la cadena de bloques con otra cadena de bloques
        if len(blockchain.chain) > len(self.chain):
            self.chain = blockchain.chain

    def validate_transaction(self, transaction):
        # Valida una transacción
        if 'amount' in transaction:
            # Si la transacción tiene un campo 'amount', validar la cantidad
            sender = transaction['sender']
            amount = transaction['amount']
            if self.get_balance(sender) >= amount:
                return True
        else:
            # Si la transacción no tiene un campo 'amount' (es un mensaje), siempre es válida
            return True
        return False

    def new_transaction(self, sender, recipient, message):
        # Crea una nueva transacción
        transaction = {
            'sender': sender,
            'recipient': recipient,
            'message': f"{sender}|{recipient}|{message}".encode()
        }
        if self.validate_transaction(transaction):
            self.current_transactions.append(transaction)
            return True
        return False

    def get_balance(self, address):
        # Obtiene el balance de una dirección
        balance = 0
        for block in self.chain:
            for transaction in block['transactions']:
                if transaction['sender'] == address:
                    balance -= transaction['amount']
                if transaction['recipient'] == address:
                    balance += transaction['amount']
        return balance

    def save_blockchain(self, filename):
        # Guarda la cadena de bloques en un archivo
        with open(filename, 'wb') as file:
            pickle.dump(self.chain, file)

    def load_blockchain(self, filename):
        # Carga la cadena de bloques desde un archivo
        try:
            with open(filename, 'rb') as file:
                self.chain = pickle.load(file)
        except (IOError, pickle.UnpicklingError):
            self.chain = []

def handle_received_message(message, chat_box, client_name, blockchain):
    # Maneja los mensajes recibidos
    try:
        message_decoded = message.decode('utf-8')  # Decodifica usando UTF-8
        parts = message_decoded.split('|')
        if len(parts) == 4:
            sender, recipient, msg, blockchain_data = parts
            # Solo muestra el mensaje, no la informacion del blockchain
            chat_box.insert(tk.END, f'{sender} -> {recipient}: {msg}\n')
            # Actualiza el blockchain (opcional)
            received_blockchain = pickle.loads(blockchain_data.encode())
            blockchain.sync_blockchain(received_blockchain)
        else:
            chat_box.insert(tk.END, f'')
    except UnicodeDecodeError as e:
        print(f"Error de decodificación: {e}")
        # Maneje aquí el error de descodificación




        
def send_and_mine(client_name, message_entry, dest_ip_entry, blockchain):
    # Envía y mina una transacción
    message = message_entry.get()
    dest_ips = dest_ip_entry.get().split(',')
    for dest_ip in dest_ips:
        if message and dest_ip:
            try:
                # Envia la transacción a la blockchain
                blockchain.new_transaction(sender=client_name, recipient=dest_ip, message=message)

                # Conectarse a la dirección IP del destinatario
                recipient_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                recipient_socket.connect((dest_ip, PORT))

                # Envia solamente el mensaje
                recipient_socket.sendall(message.encode())
                
                blockchain.save_blockchain('blockchain.dat')  # Guardar la blockchain en un archivo
                chat_box.insert(tk.END, f'Mined: {message}\n')
                recipient_socket.close()  # Cierra la conexión  
                message_entry.delete(0, tk.END)
            except Exception as e:
                messagebox.showerror("Error", f"Error: {e}")
        else:
            messagebox.showerror("Error", "Please enter a message and a valid IP address.")


def handle_peer_connection(peer_socket, chat_box, blockchain, client_name):
    # Maneja la conexión con un par
    try:
        while True:
            message = peer_socket.recv(BUFFER_SIZE)
            if not message:
                break
            handle_received_message(message, chat_box, client_name, blockchain)
            chat_box.insert(tk.END, f'Mensaje recibido: {message.decode()}\n')
           
    except Exception as e:
        print(f"Error: {e}")
    finally:
        peer_socket.close()
        connected_peers_sockets.remove(peer_socket)

def server_start(chat_box, blockchain, client_name):
    # Inicia el servidor
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(('0.0.0.0', PORT))
    server.listen(5)

    while True:
        client, addr = server.accept()
        print(f"Accepted connection from: {addr[0]}:{addr[1]}")
        connected_peers_sockets.append(client)
        client_handler = threading.Thread(target=handle_peer_connection, args=(client, chat_box, blockchain, client_name))
        client_handler.start()

def client_start(root, chat_box, client_name, blockchain):
    # Inicia el cliente
    dest_ip_label = tk.Label(root, text="IP Destinatario:")
    dest_ip_label.pack()
    dest_ip_entry = tk.Entry(root, width=30)
    dest_ip_entry.pack()

    message_label = tk.Label(root, text="Mensaje:")
    message_label.pack()
    message_entry = tk.Entry(root, width=50)
    message_entry.pack()

    send_button = tk.Button(root, text="Enviar", command=lambda: send_and_mine(client_name, message_entry, dest_ip_entry, blockchain))
    send_button.pack()

def close_all(root):
    # Cierra todas las ventanas
    if root:
        root.destroy()

if __name__ == "__main__":
    # Punto de entrada principal del programa
    root = tk.Tk()
    root.title("Chat")

    frame = tk.Frame(root)
    scrollbar = tk.Scrollbar(frame)
    chat_box = tk.Text(frame, height=15, width=50, yscrollcommand=scrollbar.set)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    chat_box.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    frame.pack()

    client_name = input("Ingresa tu nombre de usuario: ")
    root.update_idletasks()  # Actualizar la interfaz gráfica de usuario

    blockchain = Blockchain()  # Inicializar la blockchain
    blockchain.load_blockchain('blockchain.dat')  # Cargar la blockchain desde un archivo

    server_thread = threading.Thread(target=server_start, args=(chat_box, blockchain, client_name))
    server_thread.daemon = True  # Establecer el hilo del servidor como un hilo demonio
    server_thread.start()

    client_start(root, chat_box, client_name, blockchain)

    root.protocol("WM_DELETE_WINDOW", lambda: close_all(root))
    root.mainloop()

    blockchain.save_blockchain('blockchain.dat')

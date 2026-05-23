import socket
import threading
from spreedb import SpreeDB

def handle_client(client_socket, client_address, db):
    """This function runs in a separate thread for EVERY connected user."""
    client_socket.send(b"Welcome to SpreeDB Multiplayer! Type EXIT to disconnect.\n")
    
    while True:
        try:
            # Wait to receive up to 1024 bytes of data from this specific client
            data = client_socket.recv(1024).decode('utf-8').strip()
            if not data:
                break  # If data is empty, the client abruptly disconnected
            
            tokens = data.split()
            if not tokens:
                continue
                
            cmd = tokens[0].upper()
            
            # Route the network commands to our database engine
            if cmd == "EXIT":
                break
            elif cmd == "SET" and len(tokens) >= 3:
                db.set(tokens[1], tokens[2])
                client_socket.send(b"OK\n")
            elif cmd == "GET" and len(tokens) >= 2:
                val = db.get(tokens[1])
                response = f"{val}\n" if val is not None else "(nil)\n"
                client_socket.send(response.encode('utf-8'))
            elif cmd == "SAVE":
                db.save_to_disk()
                client_socket.send(b"DB Saved to Disk.\n")
            else:
                client_socket.send(b"ERR: Unknown command or bad syntax.\n")
                
        except Exception as e:
            print(f"[ERROR] Client Error ({client_address}): {e}")
            break
            
    # Clean up when they leave
    client_socket.close()
    print(f"[DISCONNECTED] Client disconnected: {client_address}")

def start_server():
    host = '127.0.0.1'
    port = 8888

    # Boot up the core database engine
    db = SpreeDB()
    db.load_from_disk()

    # Open the network socket
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind((host, port))
    server_socket.listen(5)

    print(f"[SERVER] SpreeDB Server listening on {host}:{port}...")

    # The infinite loop now ONLY accepts clients and spawns threads
    while True:
        client_socket, client_address = server_socket.accept()
        print(f"[CONNECTED] New connection established: {client_address}")
        
        # Spawn a new thread to run handle_client() for this user
        client_thread = threading.Thread(
            target=handle_client, 
            args=(client_socket, client_address, db)
        )
        client_thread.start()

if __name__ == '__main__':
    start_server()

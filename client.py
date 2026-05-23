import socket
import sys
import threading

def receive_messages(sock):
    while True:
        try:
            data = sock.recv(1024)
            if not data:
                print("\n[DISCONNECTED] Server closed the connection.")
                break
            # Print server response directly
            sys.stdout.write(data.decode('utf-8'))
            sys.stdout.flush()
        except Exception:
            break

def start_client():
    host = '127.0.0.1'
    port = 8888
    
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        sock.connect((host, port))
    except Exception as e:
        print(f"[ERROR] Could not connect to SpreeDB Server: {e}")
        return

    # Start thread to receive messages concurrently in the background
    thread = threading.Thread(target=receive_messages, args=(sock,), daemon=True)
    thread.start()

    print("[CONNECTED] Connected to SpreeDB Server. Type commands (e.g., SET x 10, GET x) or EXIT to disconnect.")
    
    while True:
        try:
            line = input().strip()
            if not line:
                continue
            sock.sendall((line + "\n").encode('utf-8'))
            if line.upper() == "EXIT":
                break
        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"[ERROR] Send error: {e}")
            break
            
    sock.close()
    print("[CLOSED] Connection closed.")

if __name__ == '__main__':
    start_client()

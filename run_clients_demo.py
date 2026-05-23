import socket
import time

def run_demo():
    host = '127.0.0.1'
    port = 8888

    print("==================================================")
    print(">>> SpreeDB Multiplayer Client Automation Demo <<<")
    print("==================================================")

    # 1. Simulate Client 1 connecting and setting a key
    print("\n[Client 1] Connecting to SpreeDB Server...")
    c1 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        c1.connect((host, port))
    except Exception as e:
        print(f"[ERROR] Could not connect Client 1: {e}")
        return
    
    # Read welcome message
    welcome1 = c1.recv(1024).decode('utf-8').strip()
    print(f"[Client 1] Server Welcome: '{welcome1}'")

    print("[Client 1] Sending: 'SET status active'")
    c1.sendall(b"SET status active\n")
    
    # Read OK response
    resp1 = c1.recv(1024).decode('utf-8').strip()
    print(f"[Client 1] Server Response: '{resp1}'")

    print("[Client 1] Disconnecting...")
    c1.sendall(b"EXIT\n")
    c1.close()

    time.sleep(1)

    # 2. Simulate Client 2 connecting and getting the key
    print("\n[Client 2] Connecting to SpreeDB Server...")
    c2 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        c2.connect((host, port))
    except Exception as e:
        print(f"[ERROR] Could not connect Client 2: {e}")
        return
    
    # Read welcome message
    welcome2 = c2.recv(1024).decode('utf-8').strip()
    print(f"[Client 2] Server Welcome: '{welcome2}'")

    print("[Client 2] Sending: 'GET status'")
    c2.sendall(b"GET status\n")
    
    # Read response
    resp2 = c2.recv(1024).decode('utf-8').strip()
    print(f"[Client 2] Server Response: '{resp2}'")

    print("[Client 2] Disconnecting...")
    c2.sendall(b"EXIT\n")
    c2.close()
    
    print("\n==================================================")
    print(">>>         Multiplayer Demo Successful!       <<<")
    print("==================================================")

if __name__ == '__main__':
    run_demo()

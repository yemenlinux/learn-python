import os
import socket
import multiprocessing
import time

def simple_server():
    """Simple socket server process"""
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind(('localhost', 8888))
    server_socket.listen(1)
    
    print("Server listening on port 8888...")
    
    while True:
        client_socket, address = server_socket.accept()
        print(f"Server: Connection from {address}")
        
        # Handle client in a separate process
        pid = os.fork()
        if pid == 0:
            # Child process handles client
            server_socket.close()  # Close in child
            
            message = f"Hello from server! Time: {time.time()}"
            client_socket.send(message.encode())
            client_socket.close()
            os._exit(0)
        else:
            client_socket.close()  # Close in parent

def simple_client():
    """Simple socket client"""
    time.sleep(1)  # Wait for server to start
    
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect(('localhost', 8888))
    
    data = client_socket.recv(1024)
    print(f"Client received: {data.decode()}")
    client_socket.close()

def socket_communication_demo():
    """Demonstrate client-server communication"""
    server_process = multiprocessing.Process(target=simple_server)
    client_process = multiprocessing.Process(target=simple_client)
    
    server_process.start()
    client_process.start()
    
    client_process.join()
    server_process.terminate()  # Stop server

socket_communication_demo()

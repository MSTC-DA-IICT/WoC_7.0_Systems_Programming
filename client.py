import socket

SERVER_HOST = '127.0.0.1'  
SERVER_PORT = 65432        
ENCODING = 'utf-8'         

def send_command(command):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
        try:
            client_socket.connect((SERVER_HOST, SERVER_PORT))
            client_socket.sendall(command.encode(ENCODING))
            
            response = client_socket.recv(1024).decode(ENCODING)
            print(f"{response}")
        except ConnectionRefusedError:
            print("Error: Unable to connect to the server. Ensure the server is running.")

def main():
    print("Available commands: ADD, REMOVE, GET, LIST ALL, SORT, EXIT")
    print("Example command for ADD: ADD John apple orange banana")
    while True:
        command = input("Enter command: ").strip()

        if command.upper() == "EXIT":
            print("Exiting...")
            break
        else:
            send_command(command)

if __name__ == "__main__":
    main()

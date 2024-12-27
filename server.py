import socket
import sqlite3
import os

HOST = '127.0.0.1' 
PORT = 65432       

DB_NAME = "data.db"
conn = None
cursor = None
db_connected = False
def display_help():
    help_message = """
Server Command Help:
--------------------
OPEN <file_path>       - Open a specific SQLite database file.
ADD <name> <string1 string2 ... stringN> - Add a new record with the given name and strings.
GET <name>             - Retrieve all strings associated with the given name.
REMOVE <name>          - Remove the record associated with the given name.
LIST ALL               - List all records in the database.
SORT <index>           - Sort records by the specified string index (1-based).
EXIT                   - Shut down the server.
--help                 - Display this help message.
"""
    return help_message

def handle_command(command):
    global conn, cursor, db_connected, DB_NAME

    parts = command.strip().split(" ")
    action = parts[0].upper()
    response = ""

    try:
        if parts[0]=="--help":
            response=display_help()
           
        elif action == "OPEN":
            if len(parts) < 2:
                response = "Error: Please specify a database file path."
                return response

            db_file_path = parts[1]
            if not os.path.exists(db_file_path):
                response = f"Error: Database file '{db_file_path}' does not exist."
                return response

            conn = sqlite3.connect(db_file_path)
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS entries (
                    name TEXT PRIMARY KEY,
                    strings TEXT
                )
            """)
            db_connected = True
            DB_NAME = db_file_path
            response = f"Connected to database: {db_file_path}"

        elif not db_connected:
            response = "Error: No database connected. Use the OPEN command first."

        elif action == "ADD":
            if len(parts) < 3:
                response = "Error: ADD requires a name and strings."
            else:
                name = parts[1]
                strings = " ".join(parts[2:])
                cursor.execute("SELECT strings FROM entries WHERE name = ?", (name,))
                existing = cursor.fetchone()

                if existing:
                    response = f"Name '{name}' already exists. Overwrite? (use REMOVE first to delete)."
                else:
                    cursor.execute("INSERT INTO entries (name, strings) VALUES (?, ?)", (name, strings))
                    response = f"Added '{name}' to the database."

        elif action == "REMOVE":
            if len(parts) < 2:
                response = "Error: REMOVE requires a name."
            else:
                name = parts[1]
                cursor.execute("DELETE FROM entries WHERE name = ?", (name,))
                response = f"Removed '{name}' from the database." if cursor.rowcount > 0 else f"No entry found with name '{name}'."

        elif action == "GET":
            if len(parts) < 2:
                response = "Error: GET requires a name."
            else:
                name = parts[1]
                cursor.execute("SELECT strings FROM entries WHERE name = ?", (name,))
                result = cursor.fetchone()
                response = f"{name}: {result[0]}" if result else f"No entry found with name '{name}'."

        elif parts[0]+" "+parts[1] == "LIST ALL":
            cursor.execute("SELECT name, strings FROM entries ORDER BY name")
            results = cursor.fetchall()
            response = "\n".join([f"{name}: {strings}" for name, strings in results]) if results else "No entries found."

        elif action == "SORT":
            if len(parts) < 2:
                response = "Error: SORT requires an index."
            else:
                index = int(parts[1])
                cursor.execute("SELECT name, strings FROM entries")
                results = cursor.fetchall()

                def extract_string(strings):
                    parts = strings.split()
                    return parts[index] if index < len(parts) else ""

                sorted_results = sorted(results, key=lambda x: extract_string(x[1]))
                response = "\n".join([f"{name}: {strings}" for name, strings in sorted_results])

        else:
            response = "Unknown command."

    except Exception as e:
        response = f"Error: {str(e)}"
    
    if conn:
        conn.commit()
    
    return response

def start_server():
    global conn, cursor, db_connected

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
        server_socket.bind((HOST, PORT))
        server_socket.listen(5)

        while True:
            client_socket, client_address = server_socket.accept()
            with client_socket:
                
                data = client_socket.recv(1024).decode('utf-8')
                if not data:
                    break
               
            
                response = handle_command(data)
                client_socket.sendall(response.encode('utf-8'))

if __name__ == "__main__":
    start_server()

import socket
import threading
import folium
import utility
import database as db
import gui
import atms_classes as atm


HEADER = 64
PORT = 12500
FORMAT = 'utf-8'
DISCONNECT_MESSAGE = "!DISCONNECT"


def client_handler(conn, address):
    print(f"[CONNECTED] Client {address} has just connected")
    connected = True
    msg_length = 0
    msg = 0
    while connected:
        try:
            msg_length = conn.recv(HEADER).decode(FORMAT)  # initially get receive data length, then receive that amount of bytes
        except ConnectionResetError:
            connected = False
        if msg_length:
            msg_length = int(msg_length)
            try:
                msg = conn.recv(msg_length).decode(FORMAT)  # get msg_length amount of bytes
            except ConnectionResetError:
                connected = False

            if msg == DISCONNECT_MESSAGE:
                connected = False
                print(f"[DISCONNECTED] Client {address} has just disconnected")

            print(f"[{address}] {msg}")

            if msg == "Get info":
                utility.send_coordinates(conn, atm.atms)
            elif msg == "Get routes for next 5 days":
                for k in range(5):
                    print(f"Send {k} html file")
                    utility.send_html(conn, atm.atms, atm.collectors, folium)
            else:
                utility.send_str(conn, "Wrong query")

    conn.close()


def start_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # AF_INET = IP, SOCK_STREAM = TCP
    server.bind(("192.168.1.69", PORT))
    server.listen()
    print("Server is listening")
    print(f"[LISTENING] Server is listening on {socket.gethostbyname(socket.gethostname())}")
    while True:
        conn, addr = server.accept()
        thread = threading.Thread(target=client_handler, args=(conn, addr))
        thread.start()


thread_0 = threading.Thread(target=gui.window)
thread_0.start()

thread_1 = threading.Thread(target=start_server)
thread_1.start()
thread_1.join()

db.connection.close()

print("Done")

import os
import socket
import sys
import threading

# from IPython.external.qt_for_kernel import QtCore
from PyQt5 import QtCore
from PyQt5 import QtWidgets
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtWidgets import QApplication, QGridLayout, QMainWindow, QWidget
from PyQt5.QtGui import QIcon

html_counter = 1
file_pointer = 1


def clicked_1():
    thread_get_html = threading.Thread(target=receive, args=["Get routes for next 5 days", 5])
    thread_get_html.start()


def clicked_2(map_instance):
    if os.path.isfile(f'./received_map_day_{file_pointer}.html'):
        map_instance.load(QtCore.QUrl().fromLocalFile(os.path.split(os.path.abspath(__file__))[0]
                                                      + rf'./received_map_day_{file_pointer}.html'))
    else:
        map_instance.load(QtCore.QUrl().fromLocalFile(os.path.split(os.path.abspath(__file__))[0]
                                                      + rf'./error_picture.jpg'))


def combo_box_on_change(value):
    global file_pointer
    file_pointer = int(value)


def window():
    app = QApplication(sys.argv)
    win = QMainWindow()
    win.setGeometry(800, 350, 1300, 1000)
    win.setWindowIcon(QIcon('map_icon.jpg'))
    win.setWindowTitle("Client")

    html_map = QWebEngineView()

    central_widget = QWidget()
    win.setCentralWidget(central_widget)

    button_1 = QtWidgets.QPushButton(win)
    button_1.setText("Get routes for next 5 days")
    button_1.clicked.connect(clicked_1)

    button_2 = QtWidgets.QPushButton(win)
    button_2.setText("Draw map")
    button_2.clicked.connect(lambda: clicked_2(html_map))

    combo_box = QtWidgets.QComboBox(win)
    combo_box.addItems(['1', '2', '3', '4', '5'])
    combo_box.activated[str].connect(combo_box_on_change)

    lay = QGridLayout(central_widget)
    lay.addWidget(html_map, 0, 0, 5, 5)
    lay.addWidget(combo_box, 5, 0)
    lay.addWidget(button_2, 5, 1)
    lay.addWidget(button_1, 5, 3)

    lay.setColumnStretch(0, 1)
    lay.setColumnStretch(1, 1)

    lay.setRowStretch(0, 1)
    lay.setRowStretch(1, 1)

    win.show()
    sys.exit(app.exec_())


HEADER = 64
PORT = 12500
FORMAT = 'utf-8'
DISCONNECT_MESSAGE = "!DISCONNECT"
SERVER = socket.gethostbyname(socket.gethostname())
ADDR = ("192.168.1.69", PORT)

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
try:
    client.connect(ADDR)
except:
    print("Connection wasn't established.")


def send_str(conn_socket, str_to_send):
    error_response = str_to_send
    send_length = str(len(error_response)).encode(FORMAT)
    send_length += b' ' * (HEADER - len(send_length))
    conn_socket.sendall(send_length)
    conn_socket.sendall(str(error_response).encode(FORMAT))


def receive(msg, quantity=1):
    if msg == "disconnect":
        send_str(client, DISCONNECT_MESSAGE)
    global html_counter
    message = msg.encode(FORMAT)
    msg_length = len(message)
    send_length = str(msg_length).encode(FORMAT)
    send_length += b' ' * (HEADER - len(send_length))
    client.send(send_length)
    client.send(message)
    for i in range(quantity):
        msg_length_new = client.recv(HEADER).decode(FORMAT)
        print(f"Message length: {msg_length_new}")
        if int(msg_length_new) > 2000:
            file = open(f'received_map_day_{html_counter}.html', "wb")
            image_chunk = client.recv(10485760)
            file.write(image_chunk)
            print(f'Got a new .html file \'received_map_day_{html_counter}.html\'!')
            html_counter = html_counter + 1 if html_counter < 5 else 1
            file.close()
        else:
            print(client.recv(int(msg_length_new)).decode(FORMAT))


thread_gui = threading.Thread(target=window())
thread_gui.start()

thread_socket = threading.Thread(target=client.connect, args=[ADDR])
thread_socket.start()

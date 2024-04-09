import sys
import utility
import database as db
import threading
import folium
import atms_classes as atm

from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QApplication, QMainWindow


def window():
    app = QApplication(sys.argv)
    win = GraphicInterface()
    win.show()
    sys.exit(app.exec_())


class GraphicInterface(QMainWindow):
    def __init__(self):
        super(GraphicInterface, self).__init__()
        self.setGeometry(300, 300, 640, 480)
        self.setWindowTitle("Server")
        self.__days_simulation_quantity = 1
        # self.combo_1 = QtWidgets.QComboBox(self)
        self.init_ui()

    def init_ui(self):
        self.label_1 = QtWidgets.QLabel(self)
        self.label_1.setText("SERVER")
        self.label_1.move(300, 50)

        self.label_2 = QtWidgets.QLabel(self)
        self.label_2.setText("")
        self.label_2.move(250, 185)

        self.button_1 = QtWidgets.QPushButton(self)
        self.button_1.setText("Refresh all ATM's")
        self.button_1.clicked.connect(self.clicked_1)
        self.button_1.move(100, 100)

        self.button_2 = QtWidgets.QPushButton(self)
        self.button_2.setText("Simulate \"n\" days")
        self.button_2.clicked.connect(self.clicked_2)
        self.button_2.move(250, 100)

        self.line_edit = QtWidgets.QLineEdit(self)
        self.line_edit.move(250, 150)

    def clicked_1(self):
        utility.full_atms_refresh(atm.atms, db.connection)

    def clicked_2(self):
        self.label_2.setText("")
        value = self.line_edit.text()
        if value.isdigit() and 0 < int(value) <= 50:
            thread_local = threading.Thread(target=utility.simulate_day_with_collectors,
                                            args=[int(value), atm.atms, atm.collectors, folium])
            thread_local.start()
        else:
            self.label_2.setText("Wrong \"days\" value")

    def switcher_1(self, input_value):
        self.__days_simulation_quantity = int(input_value)
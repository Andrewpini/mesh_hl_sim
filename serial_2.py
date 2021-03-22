import serial
import time
import sys

ser = serial.Serial()

ser.baudrate = 115200
ser.port = 'COM35'

ser.open()
# print(ser.is_open)
# s = ser.read(1)
# ser.close()
# print(ser.is_open)
# print(s)


# ser.write(str.encode("cfg gatt_cfg_link_init 49152\r\n"))
# ser.write(str.encode("cfg gatt_cfg_link_fetch 2\r\n"))
# while True:
# 	line =ser.readline()   # read a '\n' terminated line
# 	print(line)

from PyQt5 import QtCore, QtGui, QtWidgets
import socket
# from ethernetmsg import *


class SerialReadThread(QtCore.QThread):
	def __init__(self, parent=None):
		super(SerialReadThread, self).__init__(parent)

		# self.ser = serial.Serial()
		# self.ser.baudrate = 115200
		# self.ser.port = 'COM35'
		# self.ser.open()

		self.start()

    #Thread
	def run(self):
		while True:
			# print("asd")
			line =ser.readline()   # read a '\n' terminated line
			print(line)
			pass

# COMMENTED OUT UNTIL FURTHER NOTICE:
asd = SerialReadThread()

while True:
	ser.write(str.encode("cfg gatt_cfg_link_init 49152\r\n"))
	time.sleep(5)
	ser.write(str.encode("cfg gatt_cfg_link_fetch 2\r\n"))
	time.sleep(1)
	pass


class CtrlPanelWidget(object):

	def __init__(self, MainWindow):

		# --- Create main layout ---
		MainWindow.resize(1000, 700)
		MainWindow.setWindowTitle("Command Panel")
		self.centralwidget = QtWidgets.QWidget(MainWindow)
		MainWindow.setCentralWidget(self.centralwidget)

		self.prompt_window = QtWidgets.QTextEdit()
		self.prompt_window.setReadOnly(True)
		self.prompt_window.setLineWrapMode(QtWidgets.QTextEdit.NoWrap)

		self.txt_input = QtWidgets.QLineEdit()
		self.txt_input.editingFinished.connect(self.enterPress)

		# self.prompt_window.moveCursor(QtCore.QTextCursor.End)
		# self.prompt_window.setCurrentFont(font)
		# self.prompt_window.setTextColor(color)

		for item in range(100):

			self.prompt_window.insertPlainText("asd\n")

		sb = self.prompt_window.verticalScrollBar()
		sb.setValue(sb.maximum())


		font = self.prompt_window.font()
		font.setFamily("Courier")
		font.setPointSize(10)

		# --- Create Control Panel ---
		self.ctrl_widget = QtWidgets.QWidget()
		self.ctrl_widget.setMaximumSize(QtCore.QSize(350, 16777215))
		self.plot_layout = QtWidgets.QVBoxLayout(self.centralwidget)
		self.plot_layout.addWidget(self.prompt_window)
		self.slider_layout = QtWidgets.QHBoxLayout()
		self.slider_layout.addWidget(self.txt_input)
		self.plot_layout.addLayout(self.slider_layout)


	def enterPress(self):
		print("Enter pressed")
class Ui_main_widget(object):

	def __init__(self, main_widget):
		self.cpw = CtrlPanelWidget(main_widget)

# if __name__ == "__main__":
#     app = QtWidgets.QApplication(sys.argv)
#     main_widget = QtWidgets.QMainWindow()
#     ui = Ui_main_widget(main_widget)

#     main_widget.show()
#     sys.exit(app.exec_())
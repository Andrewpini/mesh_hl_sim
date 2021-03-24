import serial
import time
import sys
import math
import networkx as nx
import matplotlib.pyplot as plt
from PyQt5 import QtCore, QtGui, QtWidgets
import socket

SHELL_PROXY_INTERFACE_LINK_ENTRY = 6661
SHELL_PROXY_INTERFACE_LINK_UPDATE_STARTED = 6662
SHELL_PROXY_INTERFACE_LINK_UPDATE_ENDED = 6663

class SortedEdge(object):
	def __init__(self, node_x, node_y, initial_cnt, expected_cnt):

		self.node_x = node_x
		self.node_y = node_y
		self.received_cnt = initial_cnt
		self.expected_cnt = expected_cnt
		self.edge_quality = self.received_cnt / self.expected_cnt
		self.edge_color = None
		self.edge_color_set()

	def edge_update(self, cnt):
		self.received_cnt = (self.received_cnt + cnt) / 2
		self.edge_quality = self.received_cnt / self.expected_cnt
		self.edge_color_set()

	def edge_color_set(self):
		if self.received_cnt == self.expected_cnt:
			self.edge_color = 'g'
		elif self.received_cnt > (self.expected_cnt * 0.7):
			self.edge_color = 'b'
		else:
			self.edge_color = 'r'

class CtrlPanelWidget(QtCore.QThread):

	def __init__(self, MainWindow, parent=None):
		super(CtrlPanelWidget, self).__init__(parent)

		self.connection_network = nx.Graph()
		self.ser = serial.Serial()
		self.ser.baudrate = 115200
		self.ser.port = 'COM35'
		self.ser.open()

		self.overview = {}
		self.presence_list = []
		self.retreive_list = []

		# --- Create main layout ---
		MainWindow.resize(1000, 700)
		MainWindow.setWindowTitle("Command Panel")
		self.centralwidget = QtWidgets.QWidget(MainWindow)
		MainWindow.setCentralWidget(self.centralwidget)

		self.prompt_window = QtWidgets.QTextEdit()
		self.prompt_window.setReadOnly(True)
		self.prompt_window.setLineWrapMode(QtWidgets.QTextEdit.NoWrap)

		self.txt_input = QtWidgets.QLineEdit()
		self.txt_input.editingFinished.connect(self.enter_pressed)
		self.txt_input.textChanged.connect(self.text_changed)
		self.text = str

		# self.prompt_window.moveCursor(QtCore.QTextCursor.End)
		# self.prompt_window.setCurrentFont(font)
		# self.prompt_window.setTextColor(color)

		# for item in range(100):

		# 	self.prompt_window.insertPlainText("asd\n")

		# sb = self.prompt_window.verticalScrollBar()
		# sb.setValue(sb.maximum())


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

		self.start()

	def run(self):
		while True:
			# print("asd")
			line = self.ser.readline()   # read a '\n' terminated line
			# self.prompt_window.insertPlainText(str(line))
			# self.prompt_window.insertPlainText(line.decode("utf-8"))
			# sb = self.prompt_window.verticalScrollBar()
			# sb.setValue(sb.maximum())

			opcode = self.opcode_get(line.decode("utf-8"))
			# print("Opcode is: {}".format(opcode))
			if opcode == SHELL_PROXY_INTERFACE_LINK_ENTRY:
				self.link_map_handle(line.decode("utf-8"))
			if opcode == SHELL_PROXY_INTERFACE_LINK_UPDATE_STARTED:
				self.presence_handle(line.decode("utf-8"), self.presence_list)
				print(self.presence_list)
			if opcode == SHELL_PROXY_INTERFACE_LINK_UPDATE_ENDED:
				self.presence_handle(line.decode("utf-8"), self.retreive_list)
				print(self.retreive_list)

			print(line)
			# print(line.decode("utf-8"))
			pass


	def enter_pressed(self):
		print("Enter pressed {}".format(self.text))
		# self.ser.write(str.encode(self.text))
		if self.text == "mesh":
			self.create_edges()
			return

		if self.text == "map":
			self.data_get()
			return

		self.ser.write(str.encode("{} \r\n".format(self.text)))
		# self.ser.write(str.encode("cfg \r\n"))
		# self.ser.write(str.encode("cfg gatt_cfg_link_init 49152\r\n"))

	def text_changed(self, text):
		self.text = text

	def opcode_get(self, str_in):
		try:
			return int(str_in[:4])
		except:
			return 0

	def link_map_handle(self, str_in):

		li = list(str_in.split("-"))
		li.pop(0)
		li.pop()

		root_addr = int(li.pop(0))
		addr = int(li.pop(0))
		cnt = int(li.pop(0))

		if root_addr not in self.overview:
			self.overview[root_addr] = {}

		self.overview[root_addr][addr] = cnt
		print("Overview: {}".format(self.overview))

	def presence_handle(self, str_in, list_in):
		li = list(str_in.split("-"))
		li.pop(0)
		li.pop()
		# root_addr = int(li.pop(0))

		list_in.append(int(li.pop(0)))
		# addr = int(li.pop(0))

		# if root_addr not in self.overview:
		# 	self.overview[root_addr] = {}

		# self.overview[root_addr][addr] = cnt
		# print("Overview: {}".format(self.overview))


	def data_get(self):
		for i in self.retreive_list:
			self.ser.write(str.encode("cfg link_fetch {} \r\n".format(i)))
			time.sleep(0.5)


	def create_edges(self):
		for root_addr in self.overview:
			self.connection_network.add_node(root_addr)


		edges = self.edges_sort()

		for key, val in edges.items():
			self.connection_network.add_edge(val.node_x, val.node_y, color=val.edge_color, weight=val.edge_quality)

		# for root_addr, outer_addr in self.overview.items():
		# 	for inner_addr, cnt in outer_addr.items():
		# 		self.connection_network.add_edge(inner_addr, root_addr, color='r', weight=cnt)


		plt.clf()

		pos=nx.spring_layout(self.connection_network)
		colors = [self.connection_network[u][v]['color'] for u,v in self.connection_network.edges()]
		nx.draw_networkx(self.connection_network, pos, edge_color=colors)
		labels = nx.get_edge_attributes(self.connection_network,'weight')
		nx.draw_networkx_edge_labels(self.connection_network,pos,edge_labels=labels)

		plt.savefig("mesh.pdf", format="PDF")


	def edges_sort(self):
		edge_dict = {}

		for src_addr, ctx in self.overview.items():
			for inner_addr, cnt in ctx.items():
				id_list = [src_addr, inner_addr]
				id_list.sort()

				if str(id_list) not in edge_dict:
					edge_dict[str(id_list)] = SortedEdge(src_addr, inner_addr, cnt, 10)
				else:
					edge_dict[str(id_list)].edge_update(cnt)
		return edge_dict

class Ui_main_widget(object):

	def __init__(self, main_widget):
		self.cpw = CtrlPanelWidget(main_widget)

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    main_widget = QtWidgets.QMainWindow()
    ui = Ui_main_widget(main_widget)

    main_widget.show()
    sys.exit(app.exec_())

# G = nx.Graph()
# G.add_edge(1,2,color='r',weight=2)
# G.add_edge(2,3,color='b',weight=4)
# G.add_edge(3,4,color='y',weight=6)

# pos = nx.circular_layout(G)

# # edges = G.edges()
# colors = [G[u][v]['color'] for u,v in G.edges()]
# # weights = [G[u][v]['weight'] for u,v in edges]

# nx.draw_networkx(G, pos, edge_color=colors)
# plt.savefig("mesh.pdf", format="PDF")

# labels = nx.get_edge_attributes(self.connection_network,'weight')
# nx.draw_networkx_edge_labels(self.connection_network,pos,edge_labels=labels)

# G=nx.Graph()
# i=1
# G.add_node(i)
# G.add_node(2)
# G.add_node(3)
# G.add_edge(1,2,weight=0.5)
# G.add_edge(1,3,weight=9.8)
# # pos=nx.get_node_attributes(G,'pos')
# # pos=nx.spring_layout(G)
# # # nx.draw(G,pos)
# # nx.draw_spring(G, with_labels=1)

# # labels = nx.get_edge_attributes(G,'weight')
# # nx.draw_networkx_edge_labels(G,pos,edge_labels=labels)

# pos=nx.spring_layout(G) # pos = nx.nx_agraph.graphviz_layout(G)
# nx.draw_networkx(G,pos)
# labels = nx.get_edge_attributes(G,'weight')
# nx.draw_networkx_edge_labels(G,pos,edge_labels=labels)

# plt.savefig("mesh.pdf", format="PDF")
# # plt.savefig(<wherever>)


# asd = [[1,2],[2,3],[3,4]]

# zxc = [2,1]
# qwe = zxc.sort

# asdf = {"2,1" : "asd"}

# asdf["2,1"] =123
# asdf[str([2,1])] =123
# print(asdf)

# print(zxc)
# if zxc in asd:
# 	print("asdasd")
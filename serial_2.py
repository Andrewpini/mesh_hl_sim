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
# asd = SerialReadThread()

# while True:
# 	ser.write(str.encode("cfg gatt_cfg_link_init 49152\r\n"))
# 	time.sleep(5)
# 	ser.write(str.encode("cfg gatt_cfg_link_fetch 2\r\n"))
# 	time.sleep(1)
# 	pass

class PrefBtn(QtWidgets.QPushButton):
	def __init__(self, name, is_enabled=True, parent=None):
		super(PrefBtn, self).__init__(parent)
		self.setMinimumHeight(30)
		self.setText(name)
		self.setEnabled(is_enabled)

class CtrlPanelWidget(object):

	def __init__(self, MainWindow):

		# --- Create main layout ---
		MainWindow.resize(1000, 700)
		MainWindow.setWindowTitle("Command Panel")
		self.centralwidget = QtWidgets.QWidget(MainWindow)
		MainWindow.setCentralWidget(self.centralwidget)



		#--- Create all buttons ---
		self.time_sync_stop_btn = PrefBtn("Stop")
		self.time_sync_start_btn = PrefBtn("Start")
		self.sync_line_stop_btn = PrefBtn("Stop")
		self.sync_line_start_btn = PrefBtn("Start")
		self.led_on_btn = PrefBtn("On")
		self.led_off_btn = PrefBtn("Off")
		self.led_all_on_btn = PrefBtn("All On")
		self.led_all_off_btn = PrefBtn("All Off")
		self.dfu_single_btn = PrefBtn("DFU Selected Node")
		self.dfu_all_btn = PrefBtn("DFU All")
		self.reset_btn = PrefBtn("Reset Selected Node")
		self.reset_all_btn = PrefBtn("Reset All")
		self.tx_pwr_btn = PrefBtn("Set Selected Node")
		self.tx_pwr_all_btn = PrefBtn("Set All")
		self.clear_plot_btn = PrefBtn("Clear Plot")


		# --- Create all lists ---
		self.list_of_nodes = QtWidgets.QListWidget()
		self.list_of_nodes.setMinimumHeight(300)


		# --- Create all labels ---
		self.sync_line_label = QtWidgets.QLabel()
		self.sync_line_label.setText("Waiting for initialization")
		self.time_sync_label = QtWidgets.QLabel()
		self.time_sync_label.setText("Waiting for initialization")
		self.plot_sample_label = QtWidgets.QLabel()

		# --- Create all spaceritems ---
		self.spacer = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)


		# --- Create all combo boxes ---
		self.tx_power_cbox = QtWidgets.QComboBox()
		self.tx_power_cbox.addItem('8 Dbm')
		self.tx_power_cbox.addItem('7 Dbm')
		self.tx_power_cbox.addItem('6 Dbm')
		self.tx_power_cbox.addItem('5 Dbm')
		self.tx_power_cbox.addItem('4 Dbm')
		self.tx_power_cbox.addItem('3 Dbm')
		self.tx_power_cbox.addItem('2 Dbm')
		self.tx_power_cbox.addItem('0 Dbm')
		self.tx_power_cbox.addItem('-4 Dbm')
		self.tx_power_cbox.addItem('-8 Dbm')
		self.tx_power_cbox.addItem('-12 Dbm')
		self.tx_power_cbox.addItem('-16 Dbm')
		self.tx_power_cbox.addItem('-20 Dbm')
		self.tx_power_cbox.addItem('-30 Dbm')
		self.tx_power_cbox.addItem('-40 Dbm')


		# --- Create all plots ---
		self.txtbox = QtWidgets.QTextEdit()
		self.txtbox.setReadOnly(True)
		self.txtbox.setLineWrapMode(QtWidgets.QTextEdit.NoWrap)

		# self.txtbox.moveCursor(QtCore.QTextCursor.End)
		# self.txtbox.setCurrentFont(font)
		# self.txtbox.setTextColor(color)

		for item in range(100):

			self.txtbox.insertPlainText("asd\n")

		sb = self.txtbox.verticalScrollBar()
		sb.setValue(sb.maximum())


		font = self.txtbox.font()
		font.setFamily("Courier")
		font.setPointSize(10)
		# self.plot1 = TimeSyncPlot()
		# self.plot1.addLegend()
		# self.plot2 = TimeSyncPlot(plot_partial=True)

		# --- Create all sliders ---
		self.horizontalSlider = QtWidgets.QSlider()
		self.horizontalSlider.setMaximum(200)
		self.horizontalSlider.setMinimum(5)
		self.horizontalSlider.setValue(50)
		self.horizontalSlider.setTickInterval(10)
		self.horizontalSlider.setTickPosition(QtWidgets.QSlider.TicksBelow)
		self.horizontalSlider.setOrientation(QtCore.Qt.Horizontal)

		# ---  Create Available nodes group box ---
		self.nodes_gbox = QtWidgets.QGroupBox()
		self.nodes_gbox.setTitle("Available nodes")
		self.nodes_gbox_layout = QtWidgets.QVBoxLayout(self.nodes_gbox)
		self.nodes_gbox_layout.addWidget(self.list_of_nodes)


		#---  Create Syncronization line group box ---
		self.sync_line_gbox = QtWidgets.QGroupBox()
		self.sync_line_gbox.setTitle("Sync line")
		self.sync_line_gbox_layout = QtWidgets.QVBoxLayout(self.sync_line_gbox)
		self.sync_line_gbox_layout.addWidget(self.sync_line_label)
		self.sync_line_btn_layout = QtWidgets.QHBoxLayout()
		self.sync_line_btn_layout.addWidget(self.sync_line_start_btn)
		self.sync_line_btn_layout.addWidget(self.sync_line_stop_btn)
		self.sync_line_gbox_layout.addLayout(self.sync_line_btn_layout)


		# ---  Create Time syncronization group box ---
		self.time_sync_gbox = QtWidgets.QGroupBox()
		self.time_sync_gbox.setTitle("Time syncronization")
		self.time_sync_gbox_layout = QtWidgets.QVBoxLayout(self.time_sync_gbox)
		self.time_sync_btn_layout = QtWidgets.QHBoxLayout()
		self.time_sync_gbox_layout.addWidget(self.time_sync_label)
		self.time_sync_btn_layout.addWidget(self.time_sync_start_btn)
		self.time_sync_btn_layout.addWidget(self.time_sync_stop_btn)
		self.time_sync_gbox_layout.addLayout(self.time_sync_btn_layout)


		# ---  Create Led contoll group box ---
		self.led_gbox = QtWidgets.QGroupBox()
		self.led_gbox.setTitle("Led controller")
		self.led_gbox_layout = QtWidgets.QVBoxLayout(self.led_gbox)
		self.single_led_btn_layout = QtWidgets.QHBoxLayout()
		self.single_led_btn_layout.addWidget(self.led_on_btn)
		self.single_led_btn_layout.addWidget(self.led_off_btn)
		self.led_gbox_layout.addLayout(self.single_led_btn_layout)
		self.all_led_btn_layout = QtWidgets.QHBoxLayout()
		self.all_led_btn_layout.addWidget(self.led_all_on_btn)
		self.all_led_btn_layout.addWidget(self.led_all_off_btn)
		self.led_gbox_layout.addLayout(self.all_led_btn_layout)


		# ---  Create DFU group box ---
		self.dfu_gbox = QtWidgets.QGroupBox()
		self.dfu_gbox.setTitle("Device firmware update")
		self.dfu_gbox_layout = QtWidgets.QVBoxLayout(self.dfu_gbox)
		self.dfu_btn_layout = QtWidgets.QHBoxLayout()
		self.dfu_btn_layout.addWidget(self.dfu_single_btn)
		self.dfu_btn_layout.addWidget(self.dfu_all_btn)
		self.dfu_gbox_layout.addLayout(self.dfu_btn_layout)


		# ---  Create Reset group box ---
		self.reset_gbox = QtWidgets.QGroupBox()
		self.reset_gbox.setTitle("Reset")
		self.reset_gbox_layout = QtWidgets.QVBoxLayout(self.reset_gbox)
		self.reset_btn_layout = QtWidgets.QHBoxLayout()
		self.reset_btn_layout.addWidget(self.reset_btn)
		self.reset_btn_layout.addWidget(self.reset_all_btn)
		self.reset_gbox_layout.addLayout(self.reset_btn_layout)


		# ---  Create Tx Power group box ---
		self.tx_pwr_gbox = QtWidgets.QGroupBox()
		self.tx_pwr_gbox.setTitle("Node Tx Power")
		self.tx_pwr_gbox_layout = QtWidgets.QVBoxLayout(self.tx_pwr_gbox)
		self.tx_pwr_btn_layout = QtWidgets.QHBoxLayout()
		self.tx_pwr_btn_layout.addWidget(self.tx_pwr_btn)
		self.tx_pwr_btn_layout.addWidget(self.tx_pwr_all_btn)
		self.tx_pwr_gbox_layout.addWidget(self.tx_power_cbox)
		self.tx_pwr_gbox_layout.addLayout(self.tx_pwr_btn_layout)


		# --- Create Control Panel ---
		self.ctrl_widget = QtWidgets.QWidget()
		self.ctrl_widget.setMaximumSize(QtCore.QSize(350, 16777215))
		self.ctrl_layout = QtWidgets.QVBoxLayout(self.ctrl_widget)
		self.ctrl_layout.addWidget(self.nodes_gbox)
		self.ctrl_layout.addWidget(self.sync_line_gbox)
		self.ctrl_layout.addWidget(self.time_sync_gbox)
		self.ctrl_layout.addWidget(self.led_gbox)
		self.ctrl_layout.addWidget(self.dfu_gbox)
		self.ctrl_layout.addWidget(self.reset_gbox)
		self.ctrl_layout.addWidget(self.tx_pwr_gbox)


		# --- Create plot layout ---
		self.plot_layout = QtWidgets.QVBoxLayout(self.centralwidget)
		self.plot_layout.addWidget(self.txtbox)
		# self.plot_layout.addWidget(self.plot1)
		# self.plot_layout.addWidget(self.plot2)
		self.plot_layout.addWidget(self.plot_sample_label)
		self.slider_layout = QtWidgets.QHBoxLayout()
		self.slider_layout.addWidget(self.horizontalSlider)
		self.slider_layout.addWidget(self.clear_plot_btn)
		# self.slider_layout.addItem(self.spacer)
		self.plot_layout.addLayout(self.slider_layout)

		self.ctrl_dock = QtWidgets.QDockWidget(MainWindow)
		self.ctrl_dock.setWindowTitle('Controller')
		self.ctrl_dock.setFeatures(QtWidgets.QDockWidget.DockWidgetFloatable | QtWidgets.QDockWidget.DockWidgetMovable)
		self.ctrl_dock.setAllowedAreas(QtCore.Qt.LeftDockWidgetArea | QtCore.Qt.RightDockWidgetArea)
		MainWindow.addDockWidget(QtCore.Qt.DockWidgetArea(1), self.ctrl_dock)
		self.ctrl_dock.setWidget(self.ctrl_widget)

		# Makes sure that the right widgets are not clickable at initialization point
		self.set_clickable_widgets(False)

	# TODO: Improve the enabling/disabling of the buttons
	def set_clickable_widgets(self, on_off):
		self.sync_line_gbox.setEnabled(on_off)
		self.time_sync_gbox.setEnabled(on_off)
		self.led_on_btn.setEnabled(on_off)
		self.led_off_btn.setEnabled(on_off)
		self.dfu_single_btn.setEnabled(on_off)
		self.reset_btn.setEnabled(on_off)
		self.tx_pwr_btn.setEnabled(on_off)

class Ui_main_widget(object):

	def __init__(self, main_widget):
	# self.selected_item = NodeEntry
	# self.current_time_sync_node = 'None'
	# self.current_sync_line_node = 'None'
	# self.node_list = NodeList(1000)
	# TODO: Dynamicaly update node cnt
	# self.parser = SampleParser(2, 2)
		self.cpw = CtrlPanelWidget(main_widget)
	# self.connect_widgets()
	# self.cpw.plot_sample_label.setText('Samples shown: %d' % self.cpw.horizontalSlider.value())

	# # Create ethernet communication instance and connect signals to corresponding handlers
	# self.ethernet = ethernetcomm.EthernetCommunicationThread("0.0.0.0", 11001, "255.255.255.255", 10000)

	# self.ethernet.sig_i_am_alive.connect(self.i_am_alive_msg_handler)
	# self.ethernet.sig_ack_msg.connect(self.ack_msg_handler)
	# self.ethernet.sig_sync_line_sample_msg.connect(self.handle_time_sync_sample)
	# self.node_list.node_list_timeout_sig.connect(self.node_list_timeout_handler)
	# self.parser.plot_signal.connect(self.handle_parser_output)



#     def connect_widgets(self):
#         self.cpw.list_of_nodes.currentItemChanged.connect(self.on_item_changed)
#         self.cpw.time_sync_start_btn.clicked.connect(self.send_time_sync_start_msg)
#         self.cpw.time_sync_stop_btn.clicked.connect(self.send_time_sync_stop_msg)
#         self.cpw.sync_line_start_btn.clicked.connect(self.send_sync_line_start_msg)
#         self.cpw.sync_line_stop_btn.clicked.connect(self.send_sync_line_stop_msg)
#         self.cpw.led_on_btn.clicked.connect(lambda: self.send_led_msg(False, True, self.selected_item.mac_addr))
#         self.cpw.led_off_btn.clicked.connect(lambda: self.send_led_msg(False, False, self.selected_item.mac_addr))
#         self.cpw.led_all_on_btn.clicked.connect(lambda: self.send_led_msg(True, True, None))
#         self.cpw.led_all_off_btn.clicked.connect(lambda: self.send_led_msg(True, False, None))
#         self.cpw.dfu_single_btn.clicked.connect(lambda: self.send_dfu_msg(False, self.selected_item.mac_addr))
#         self.cpw.dfu_all_btn.clicked.connect(lambda: self.send_dfu_msg(True, None))
#         self.cpw.reset_btn.clicked.connect(lambda: self.send_reset_msg(False, self.selected_item.mac_addr))
#         self.cpw.reset_all_btn.clicked.connect(lambda: self.send_reset_msg(True, None))
#         self.cpw.tx_pwr_btn.clicked.connect(lambda: self.send_tx_pwr_msg(False, self.selected_item.mac_addr))
#         self.cpw.tx_pwr_all_btn.clicked.connect(lambda: self.send_tx_pwr_msg(True, None))
#         self.cpw.horizontalSlider.valueChanged.connect(lambda: self.cpw.plot2.set_partial_sampleset_cnt(self.cpw.horizontalSlider.value()))
#         self.cpw.horizontalSlider.valueChanged.connect(lambda: self.cpw.plot_sample_label.setText('Samples shown: %d' % self.cpw.horizontalSlider.value()))
#         self.cpw.clear_plot_btn.clicked.connect(self.handle_clear_plot)

#     def i_am_alive_msg_handler(self, msg):
#         new = self.node_list.add_node(msg)
#         if new is not None:
#             self.cpw.list_of_nodes.addItem(new)

#     def on_item_changed(self, curr, prev):

#         self.selected_item = curr.data(1)
#         self.cpw.list_of_nodes.setCurrentItem(curr)
#         if self.selected_item.is_active_node:
#             self.cpw.set_clickable_widgets(True)
#         else:
#             self.cpw.set_clickable_widgets(False)

#     def send_sync_line_start_msg(self):
#         msg = StartSyncLineMsg().get_packed_msg(self.selected_item.mac_addr)
#         self.ethernet.broadcast_data(msg)
#         self.cpw.sync_line_label.setText('Starting - Waiting for response from node %s' % self.selected_item.ip_addr)
#         self.current_sync_line_node = self.selected_item.ip_addr

#         # Set new sync master for the parser
#         self.parser.change_sync_master(str(self.selected_item.mac_addr))

#         # Reset the plot if a new sync line master msg, I. e. the user starts a new session
#         self.cpw.plot1.reset_plotter()
#         self.cpw.plot2.reset_plotter()
#         self.cpw.plot1.clear_entire_plot()
#         self.cpw.plot2.clear_entire_plot()

#     def send_sync_line_stop_msg(self):
#         msg = StopSyncLineMsg().get_packed_msg(self.selected_item.mac_addr)
#         self.ethernet.broadcast_data(msg)
#         self.cpw.sync_line_label.setText('Stopping - Waiting for response from node %s' % self.current_sync_line_node)


#     def send_time_sync_start_msg(self):
#         msg = StartTimeSyncMsg().get_packed_msg(self.selected_item.mac_addr)
#         self.ethernet.broadcast_data(msg)
#         self.cpw.time_sync_label.setText('Starting - Waiting for response from node %s' % self.selected_item.ip_addr)
#         self.current_time_sync_node = self.selected_item.ip_addr

#     def send_time_sync_stop_msg(self):
#         msg = StopTimeSyncMsg().get_packed_msg(self.selected_item.mac_addr)
#         self.ethernet.broadcast_data(msg)
#         self.cpw.time_sync_label.setText('Stopping - Waiting for response from node %s' % self.current_time_sync_node)

#     def send_led_msg(self, is_broadcast, on_off, target_addr):
#         ting = LedMsg().get_packed_msg(is_broadcast, on_off, target_addr)
#         self.ethernet.broadcast_data(ting)

#     def send_dfu_msg(self, is_broadcast, target_addr):
#         ting = DfuMsg().get_packed_msg(is_broadcast, target_addr)
#         self.ethernet.broadcast_data(ting)

#     def send_reset_msg(self, is_broadcast, target_addr):
#         ting = ResetMsg().get_packed_msg(is_broadcast, target_addr)
#         self.cpw.sync_line_label.setText('Reset has been pressed! Behaviour of sync line uncertain...')
#         self.cpw.time_sync_label.setText('Reset has been pressed! Behaviour of time sync uncertain...')
#         self.ethernet.broadcast_data(ting)


#     def send_tx_pwr_msg(self, is_broadcast, target_addr):
#         ting = TxPowerMsg().get_packed_msg(is_broadcast, self.cpw.tx_power_cbox.currentIndex(), target_addr)
#         self.ethernet.broadcast_data(ting)

#     def ack_msg_handler(self, msg):
#         if msg.ack_opcode == OPCODES['StartSyncLineMsg']:
#             self.cpw.sync_line_label.setText('Current sync line master is node %s' % msg.sender_mac_addr)
#         if msg.ack_opcode == OPCODES['StopSyncLineMsg']:
#             self.cpw.sync_line_label.setText('Sync line was stopped by user')
#         if msg.ack_opcode == OPCODES['StartTimeSyncMsg']:
#             self.cpw.time_sync_label.setText('Current time sync master is node %s' % msg.sender_mac_addr)
#         if msg.ack_opcode == OPCODES['StopTimeSyncMsg']:
#             self.cpw.time_sync_label.setText('Time sync was stopped by user')

#     def handle_time_sync_sample(self, msg):
#         if self.parser.current_sync_master is not None:
#             self.parser.add_sample(RawSample(msg.sample_nr, str(msg.mac), msg.sample_val))
#         else:
#             # print('Debug info: Sync master is not set in the parser. Reset all nodes and choose a sync line master')
#             pass


#     def handle_slider_event(self):
#         slider_val = self.cpw.horizontalSlider.value()
#         self.cpw.plot2.set_partial_sampleset_cnt(slider_val)
#         self.cpw.plot_sample_label.setText('Samples shown: %d' % slider_val)

#     def node_list_timeout_handler(self):
#         try:
#             if self.selected_item.is_active_node:
#                 self.cpw.set_clickable_widgets(True)
#             else:
#                 self.cpw.set_clickable_widgets(False)
#         except:
#             pass

#     def handle_clear_plot(self):
#         self.cpw.plot1.clear_entire_plot()
#         self.cpw.plot2.clear_entire_plot()


#     def handle_parser_output(self, nr, dicti):
#         self.cpw.plot1.add_plot_sample(nr, dicti)
#         self.cpw.plot2.add_plot_sample(nr, dicti)

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    main_widget = QtWidgets.QMainWindow()
    ui = Ui_main_widget(main_widget)




    main_widget.show()
    sys.exit(app.exec_())

import os
import csv
from datetime import datetime

TEST_RES_DIR = "test_results"
ADV_RES_FILE_NAME ="adv_bearer_results.csv"

class TestResults(object):

	def __init__(self):
		self.date_string = datetime.now().strftime("%d-%m-%Y_%H-%M-%S")
		self.dir_path = "{}/{}".format(TEST_RES_DIR, self.date_string)
		self.csv_path = "./{}/{}".format(self.dir_path, ADV_RES_FILE_NAME)

		self.create_folder()

	def create_folder(self):
		try:
			os.mkdir(self.dir_path)
		except OSError:
			print ("Creation of the directory %s failed" % self.dir_path)
		else:
			print ("Successfully created the directory %s " % self.dir_path)

	def write_adv_bearer(self, line):
		with open(self.csv_path, 'a', newline='') as file:
			writer = csv.writer(file)
			writer.writerow(line)
			file.close()

	def write_test_result(self, origin_node, msg_cnt, uniform_loss_chance, retransmit, res_dict):

		self.write_adv_bearer(["Origin node", "Message count", "Uniform Packet loss chance in %", "Transmition per relay"])
		self.write_adv_bearer([origin_node, msg_cnt, uniform_loss_chance, retransmit])
		for _ in range(4):
			self.write_adv_bearer([])

		self.write_adv_bearer(["Node", "Nr links", "Nr adjacent node", "Tot loss chance", "Timestamp last msg",
                         "Packets recived", "Packets lost", "Packet loss %", "Peak Buffer size"])

		for x, y in res_dict.items():
			packet_loss = msg_cnt - y["msg_received"]
			packet_loss_perc = packet_loss / msg_cnt * 100
			self.write_adv_bearer(
				[x, y["link_cnt"], y["adj_cnt"], y["mean_noise"], y["last_ts"], y["msg_received"], packet_loss, packet_loss_perc, y["peak_buf_size"]])


		# for item in res_list:
		# 	packet_loss = msg_cnt - item[4]
		# 	packet_loss_perc = packet_loss / msg_cnt * 100
		# 	self.write_adv_bearer(
		# 		[item[0], item[1], item[2], item[3], item[4], packet_loss, packet_loss_perc, item[5]])



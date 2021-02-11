
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

	def write_test_result(self, origin_node, msg_cnt, packet_loss, retransmit, res_list):

		self.write_adv_bearer(["Origin node", "Message count", "Packet loss chance in %", "Retransmition per relay"])
		self.write_adv_bearer([origin_node, msg_cnt, packet_loss, retransmit])
		for _ in range(4):
			self.write_adv_bearer([])

		self.write_adv_bearer(["Node", "Timestamp last msg",
                         "Packets recived", "Packets lost", "Packet loss %"])

		for item in res_list:
			packet_loss = msg_cnt - item[2]
			packet_loss_perc = packet_loss / msg_cnt * 100
			self.write_adv_bearer(
				[item[0], item[1], item[2], packet_loss, packet_loss_perc])



# Python program to demonstrate
# writing to CSV

import os
import csv
from datetime import datetime

TEST_RES_DIR = "test_results"
ADV_RES_FILE_NAME ="adv_bearer_results.csv"

class TestResults(object):

	def __init__(self):
		self.create_folder()
		self.create_csv()

	def create_folder(self):
		self.date_string = datetime.now().strftime("%d-%m-%Y_%H-%M-%S")
		self.dir_path = "{}/{}".format(TEST_RES_DIR, self.date_string)

		try:
			os.mkdir(self.dir_path)
		except OSError:
			print ("Creation of the directory %s failed" % self.dir_path)
		else:
			print ("Successfully created the directory %s " % self.dir_path)

	def create_csv(self):
		self.csv_path = "./{}/{}".format(self.dir_path, ADV_RES_FILE_NAME)

		# with open(self.csv_path, 'w', newline='') as file:
		# 	writer = csv.writer(file)
			# writer.writerow(["SN", "Name", "Contribution"])
			# writer.writerow([1, "Linus Torvalds", "Linux Kernel"])
			# writer.writerow([2, "Tim Berners-Lee", "World Wide Web"])
			# writer.writerow([3, "Guido van Rossum", "Python Programming"])

	def write_adv_bearer(self, line):
		with open(self.csv_path, 'a', newline='') as file:
			writer = csv.writer(file)
			writer.writerow(line)
			file.close()

	def write_adv_header(self, origin_node, msg_cnt, packet_loss, retransmit):
		self.write_adv_bearer(["Origin node", "Message count", "Packet loss chance in %", "Retransmition per relay"])
		self.write_adv_bearer([origin_node, msg_cnt, packet_loss, retransmit])
		for _ in range(4):
			self.write_adv_bearer([])

	def write_adv_body(self, tot_msg_cnt, res_list):
		self.write_adv_bearer(["Node", "Timestamp last msg", "Packets recived", "Packets lost", "Packet loss %"])

		for item in res_list:

			packet_loss = tot_msg_cnt - item[2]
			packet_loss_perc = packet_loss / tot_msg_cnt * 100
			self.write_adv_bearer([item[0], item[1], item[2], packet_loss, packet_loss_perc])

	def write_adv_bearer_full(self, origin_node, msg_cnt, packet_loss, retransmit, res_list):
		self.write_adv_header(origin_node, msg_cnt, packet_loss, retransmit)
		self.write_adv_body(msg_cnt, res_list)





# asd = []

# x = 0
# y = 0

# for item in range(10):
# 	asd.append([item, x, y])
# 	x += 10
# 	y += 100

# a = TestResults()
# a.write_adv_bearer_full(0, 1000, 10, 3, asd)




# a.write_adv_header(0,1000,10,3)
# a.write_adv_body(asd)
# a.write_adv_bearer(["Msg_cnt", "Pacet_loss %", "Retransmitions"])
# a.write_adv_bearer([1000, 10, 3])

# # datetime object containing current date and time
# now = datetime.now()
# dt_string = now.strftime("%d-%m-%Y_%H-%M-%S")

# # define the name of the directory to be created
# path = "{}/{}".format(TEST_RES_DIR,dt_string)

# try:
#     os.mkdir(path)
# except OSError:
#     print ("Creation of the directory %s failed" % path)
# else:
#     print ("Successfully created the directory %s " % path)

# file_path = "./{}/innovators.csv".format(path)
# with open(file_path, 'w', newline='') as file:
#     writer = csv.writer(file)
#     writer.writerow(["SN", "Name", "Contribution"])
#     writer.writerow([1, "Linus Torvalds", "Linux Kernel"])
#     writer.writerow([2, "Tim Berners-Lee", "World Wide Web"])
#     writer.writerow([3, "Guido van Rossum", "Python Programming"])



# import csv
# with open('innovators.csv', 'w', newline='') as file:
#     writer = csv.writer(file)
#     writer.writerow(["SN", "Name", "Contribution"])
#     writer.writerow([1, "Linus Torvalds", "Linux Kernel"])
#     writer.writerow([2, "Tim Berners-Lee", "World Wide Web"])
#     writer.writerow([3, "Guido van Rossum", "Python Programming"])


# with open('innovators.csv', 'r') as file:
#     reader = csv.reader(file)
#     for row in reader:
#         print(row)